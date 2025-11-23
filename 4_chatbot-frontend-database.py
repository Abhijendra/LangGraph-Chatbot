import streamlit as st 
import logging
from langgraph_tool_backend import chatbot, get_all_threads
from langchain_core.messages import HumanMessage
import uuid  
from datetime import datetime
from utilities import assign_topic, save_topic, load_topics
import os

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

# ********************************** Utility functions ****************************************

def generate_thread_id():
    logger.info('Generating new thread id.')
    thread_id = uuid.uuid4()
    logger.info(f'Generated new thread id: {thread_id} successfully.')
    return thread_id 

def reset_chat():
    logger.info('Resetting chat screen started.')
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    # cleaning message history
    st.session_state['message_history'] = []
    # adding new thread id to chat_threads of session_state
    add_thread(thread_id=st.session_state['thread_id'])
    logger.info('Resetting chat screen completed successfully.')


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        logger.info(f"Adding thread id {thread_id} to chat_threads started.")
        st.session_state['chat_threads'].append(thread_id)
        logger.info(f"Added thread id {thread_id} to chat_threads successfully.")

def load_conversation(thread_id):
    logger.info(f'Loading conversations of thread id: {thread_id}')
    state = chatbot.get_state({'configurable': {'thread_id':thread_id}})
    return state.values.get('messages', [])

# ********************************** Session Setup **************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = get_all_threads()

if 'chat_topics' not in st.session_state:
    st.session_state['chat_topics'] = load_topics()

add_thread(thread_id=st.session_state['thread_id'])
    

# ********************************** SideBar UI ****************************************

st.sidebar.title('Our Personal Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()
    
st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    topic_name = st.session_state['chat_topics'].get(thread_id,'Untitled')
    if st.sidebar.button(topic_name, key=thread_id):
        messages = load_conversation(thread_id)
        st.session_state['thread_id'] = thread_id

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role':role, 'content':msg.content})
    
        st.session_state['message_history'] = temp_messages

if topic_name == "Untitled" and len(st.session_state['message_history']) >= 2:
    topic_name = assign_topic(st.session_state['message_history'])
    st.session_state['chat_topics'][st.session_state['thread_id']] = topic_name
    char_length = save_topic(st.session_state['thread_id'], topic_name)
    if char_length:
        logger.info(f"Topic name {topic_name} saved successfully to csv file.")
    else:
        logger.info("Topic name not saved to csv due to unknown reason.")


# ********************************** Main UI *******************************************

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Ask a question')    


if user_input:
    logger.info(f"Received user input: {user_input[:50]}...")

    CONFIG = {'configurable': {'thread_id':st.session_state['thread_id']}}
    try:
        st.session_state['message_history'].append({'role':'user','content':user_input})

        with st.chat_message('user'):
            st.text(user_input)

        with st.chat_message('assistant'):
            logger.debug("Streaming chatbot messages.")
            stream_generator = chatbot.stream(
            {'messages':[HumanMessage(content=user_input)]}, 
            config=CONFIG,
            stream_mode='messages'           
            )
            
            llm_response = st.write_stream(message_chunk.content for message_chunk, metadata in stream_generator)

            st.session_state['message_history'].append({'role':'assistant','content':llm_response})



    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}", exc_info=True)
        st.error("An error occurred while processing your request. Please try again.") 