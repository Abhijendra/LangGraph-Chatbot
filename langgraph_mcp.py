from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import os 
import logging
from datetime import datetime
import sqlite3
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
import asyncio 
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# -------------------
# 0. Logging
# -------------------

ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'True').lower() == 'true'

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = f"{log_dir}/backend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO if ENABLE_LOGGING else logging.CRITICAL + 1,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ] if ENABLE_LOGGING else [logging.NullHandler()]
)

logger = logging.getLogger(__name__)


# -------------------
# 1. MCP Client
# -------------------

# Client starts the server in STDIO localhost
SERVERS = {
    "ArithmeticCalculator": {
        "transport": "stdio",
        "command": "/home/abhijendra/Projects/CampusX-MCP/arithmetic-mcp-server/.venv/bin/fastmcp", 
        "args": [
            "run",
            "/home/abhijendra/Projects/CampusX-MCP/arithmetic-mcp-server/main.py"
        ]
    },
    "Expense": {
        "transport": "streamable_http", # if this fails try sse
        "url": "https://river-cyan-fish.fastmcp.app/mcp"
    }
}

client = MultiServerMCPClient(SERVERS)

# -------------------
# 2. Checkpointer
# -------------------
# Creating SQLite connection object
try:
    logger.info("Creating sqlite DB connection for persistant memory.") 
    db_path = os.path.join("db_files","chatbot.db")
    conn = sqlite3.connect(database=db_path, check_same_thread=False)
except Exception as e:
    logger.error(f"Failed to connect with sqlite DB. Error: {str(e)}", exc_info=True)
    raise 


# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],  add_messages] 


# -------------------
# 4. LLM
# -------------------
try:
    # model_name = 'meta-llama/Llama-3.2-3B-Instruct'
    # logger.info(f"Initializing LLM model with {model_name}")
    # llm = HuggingFaceEndpoint(
    # repo_id="meta-llama/Llama-3.2-3B-Instruct",  
    # task='text-generation'
    # )
    # model = ChatHuggingFace(llm=llm)

    model_name = "gpt-4o-mini"
    logger.info(f"Initializing LLM model with {model_name}")
    model = ChatOpenAI(model=model_name)
    # llm_with_tools = model.bind_tools(tools)
except Exception as e:
    logger.error(f"Failed to initiated LLM model {model_name}. Error: {str(e)}", exc_info=True)
    raise 

# Initialize checkpointer
# logger.info("Initializing persistant checkpointer: SqliteSaver")
# try:
#     checkpointer = SqliteSaver(conn=conn)
# except Exception as e:
#     logger.error(f"Failed to initialize memory saver. {str(e)}", exc_info=True)
#     raise

async def build_graph():
    
    tools = await client.get_tools()

    logger.info("Fetched Tools from MCP Server:")

    for i, tool in enumerate(tools):
        logger.info(f"{i+1}. {tool.name}")

    llm_with_tools = model.bind_tools(tools)

    # -------------------
    # 4. Nodes
    # -------------------
    async def chat_node(state:ChatState):
        logger.debug("Entering chat_node")
        try:
            # take user query from state
            messages = state['messages']
            logger.info(f"Processing messages: {len(messages)} message(s) received")
            
            # send to llm 
            logger.debug("Invoking LLM with messages")
            response = await llm_with_tools.ainvoke(messages)
            tool_calls = getattr(response, "tool_calls", None)
            if not tool_calls:
                logger.info(f"LLM response: {response.content[:50]}...")
            else:
                logger.info(f"LLM used a tool {tool_calls[0]["name"]} for this question.")
            # store the response in state
            logger.debug("Returning updated state with LLM response")
            return {'messages':[response]}
        except Exception as e:
            logger.error(f"Error in chat_node: {str(e)}", exc_info=True)
            raise

    tool_node = ToolNode(tools) # This is already async -> handled by langgraph

    logger.info("Building and compiling StateGraph")
    try:
        graph = StateGraph(ChatState)
        graph.add_node('chat_node',chat_node)
        graph.add_node("tools", tool_node)

        graph.add_edge(START, 'chat_node')
        graph.add_conditional_edges("chat_node",tools_condition)
        graph.add_edge('tools','chat_node')

        # chatbot = graph.compile(checkpointer=checkpointer)
        chatbot = graph.compile()
        logger.info("StateGraph successfully compiled")
    except Exception as e:
        logger.error(f"Error compiling StateGraph: {str(e)}", exc_info=True)
        raise

    return chatbot 

# def get_all_threads() -> list:
#         all_threads = set()
#         thread_lst = []
#         for checkpoint in checkpointer.list(None):
#             all_threads.add(checkpoint.config['configurable']['thread_id'])
#             if len(all_threads):
#                 thread_lst = list(all_threads)
#         logger.info(f"Found {len(thread_lst)} unique threads in checkpointer")
#         return thread_lst 

async def main():
    chatbot = await build_graph()
    result = await chatbot.ainvoke({"messages":[HumanMessage(content="Find the product of 24 and 5 and report to it like a very drunken person")]})
    logger.info(f"LLM Replied: {result["messages"][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())