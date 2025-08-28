import streamlit as st 
import logging
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# 1. Get a Logger Instance
logger = logging.getLogger(__name__)
# 2. Set the Logging Level
logger.setLevel(logging.DEBUG)

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

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # final_state = chatbot.invoke({'messages':[HumanMessage(content=user_input)]}, config=CONFIG)
    # llm_response = final_state['messages'][-1].content

    with st.chat_message('assistant'):

        stream_generator = chatbot.stream(
        {'messages':[HumanMessage(content=user_input)]}, 
        config={'configurable': {'thread_id':'1'}},
        stream_mode='messages'           
        )
        
        llm_response = st.write_stream(message_chunk.content for message_chunk, metadata in stream_generator)

        st.session_state['message_history'].append({'role':'assistant','content':llm_response})
