from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import os 
import logging
from datetime import datetime
import sqlite3


load_dotenv()

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

# Creating SQLite connection object
try:
    logger.info("Creating sqlite DB connection for persistant memory.") 
    conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
except Exception as e:
    logger.error(f"Failed to connect with sqlite DB. Error: {str(e)}", exc_info=True)
    raise 


class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],  add_messages] 

try:
    logger.info("Initializing ChatOpenAI model with gpt-4o-mini")
    model_name = 'gpt-4o-mini'
    model = ChatOpenAI(model=model_name)
except Exception as e:
    logger.error(f"Failed to initiated ChatOpenAI with model {model_name}. Error: {str(e)}", exc_info=True)
    raise 


def chat_node(state:ChatState):
    logger.debug("Entering chat_node")
    try:
        # take user query from state
        messages = state['messages']
        logger.info(f"Processing messages: {len(messages)} message(s) received")
        
        # send to llm 
        logger.debug("Invoking LLM with messages")
        response = model.invoke(messages).content
        logger.info(f"LLM response: {response[:50]}...")

        # store the response in state
        logger.debug("Returning updated state with LLM response")
        return {'messages':[response]}
    except Exception as e:
        logger.error(f"Error in chat_node: {str(e)}", exc_info=True)
        raise

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
    graph.add_edge(START, 'chat_node')
    graph.add_edge('chat_node', END)
    chatbot = graph.compile(checkpointer=checkpointer)
    logger.info("StateGraph successfully compiled")
except Exception as e:
    logger.error(f"Error compiling StateGraph: {str(e)}", exc_info=True)
    raise

# try:
#     final_state = chatbot.invoke({'messages':'I am referring to a dog who loves me the most and plays with me.'},config={'configurable':{'thread_id':"1"}})
#     logger.info(final_state)
# except Exception as e:
#     logger.error(f"Error compiling StateGraph: {str(e)}", exc_info=True)
#     raise

# all_threads = set()
# for checkpointer in checkpointer.list(None):
    # print(checkpointer.config['configurable']['thread_id'])
    # all_threads.add(checkpointer.config['configurable']['thread_id'])

# print(list(all_threads))

def get_all_threads() -> list:
    all_threads = set()
    thread_lst = []
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
        if len(all_threads):
            thread_lst = list(all_threads)
    logger.info(f"Found {len(thread_lst)} unique threads in checkpointer")
    return thread_lst    
