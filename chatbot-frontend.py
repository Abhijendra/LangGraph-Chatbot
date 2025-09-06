import streamlit as st 
import logging
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
from datetime import datetime
import os

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

thread_id = '1'
CONFIG = {'configurable': {'thread_id':thread_id}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    logger.info('Loading the message history')
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Ask a question')    

if user_input:
    logger.info(f"Received user input: {user_input[:50]}...")
    try:
        st.session_state['message_history'].append({'role':'user','content':user_input})
        with st.chat_message('user'):
            st.text(user_input)

        logger.debug("Invoking chatbot with user input")
        final_state = chatbot.invoke({'messages':[HumanMessage(content=user_input)]}, config=CONFIG)
        llm_response = final_state['messages'][-1].content
        logger.info(f"Chatbot response: {llm_response[:50]}...")

        st.session_state['message_history'].append({'role':'assistant','content':llm_response})
        with st.chat_message('assistant'):
            st.text(llm_response)

    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}", exc_info=True)
        st.error("An error occurred while processing your request. Please try again.")
