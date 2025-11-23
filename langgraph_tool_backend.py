from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import BaseMessage
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
# 1. Tools
# -------------------

# Tool 1
search_tool = DuckDuckGoSearchRun(region="us-en") 

# Tool 2
@tool
def getStockPrice(symbol:str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') using Alpha Vantage with API key in the URL.
    """
    logging.info("getStockPrice Tool called.")
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    res = requests.get(url)
    return res.json()

tools = [search_tool, getStockPrice]

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
    model_name = 'meta-llama/Llama-3.2-3B-Instruct'
    logger.info(f"Initializing LLM model with {model_name}")
    # model = ChatOpenAI(model=model_name)
    # model = ChatGoogleGenerativeAI(model=model_name)
    llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.2-3B-Instruct",  
    task='text-generation'
    )
    model = ChatHuggingFace(llm=llm)
    llm_with_tools = model.bind_tools(tools)
except Exception as e:
    logger.error(f"Failed to initiated LLM model {model_name}. Error: {str(e)}", exc_info=True)
    raise 

# -------------------
# 4. Nodes
# -------------------
def chat_node(state:ChatState):
    logger.debug("Entering chat_node")
    try:
        # take user query from state
        messages = state['messages']
        logger.info(f"Processing messages: {len(messages)} message(s) received")
        
        # send to llm 
        logger.debug("Invoking LLM with messages")
        response = llm_with_tools.invoke(messages)
        logger.info(f"LLM response: {response.content[:50]}...")

        # store the response in state
        logger.debug("Returning updated state with LLM response")
        return {'messages':[response]}
    except Exception as e:
        logger.error(f"Error in chat_node: {str(e)}", exc_info=True)
        raise

tool_node = ToolNode(tools)

# Initialize checkpointer
logger.info("Initializing persistant checkpointer: SqliteSaver")
try:
    checkpointer = SqliteSaver(conn=conn)
except Exception as e:
    logger.error(f"Failed to initialize memory saver. {str(e)}", exc_info=True)
    raise

logger.info("Building and compiling StateGraph")
try:
    graph = StateGraph(ChatState)
    graph.add_node('chat_node',chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, 'chat_node')
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge('chat_node', END)

    chatbot = graph.compile(checkpointer=checkpointer)
    logger.info("StateGraph successfully compiled")
except Exception as e:
    logger.error(f"Error compiling StateGraph: {str(e)}", exc_info=True)
    raise

def get_all_threads() -> list:
    all_threads = set()
    thread_lst = []
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
        if len(all_threads):
            thread_lst = list(all_threads)
    logger.info(f"Found {len(thread_lst)} unique threads in checkpointer")
    return thread_lst    