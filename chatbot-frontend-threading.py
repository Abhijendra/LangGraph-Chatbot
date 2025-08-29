import streamlit as st 
import logging
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid  # generate a random thread-id

# ********************************** Utility functions ****************************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id 

# 1. Get a Logger Instance
logger = logging.getLogger(__name__)
# 2. Set the Logging Level
logger.setLevel(logging.DEBUG)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    # cleaning message history
    st.session_state['message_history'] = []
    # adding new thread id to chat_threads of session_state
    add_thread(thread_id=st.session_state['thread_id'])


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)



# ********************************** Session Setup **************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
    add_thread(thread_id=st.session_state['thread_id'])

    

# ********************************** SideBar UI ****************************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()
    

st.sidebar.header('My Conversations')

for i in range(len(st.session_state['chat_threads'])-1,-1,-1):
    st.sidebar.button(str(st.session_state['chat_threads'][i]))



# ********************************** Main UI *******************************************

for message in st.session_state['message_history']:
    logger.info('Loading the message history')
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Ask a question')    


if user_input:

    CONFIG = {'configurable': {'thread_id':st.session_state['thread_id']}}

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # final_state = chatbot.invoke({'messages':[HumanMessage(content=user_input)]}, config=CONFIG)
    # llm_response = final_state['messages'][-1].content

    with st.chat_message('assistant'):

        stream_generator = chatbot.stream(
        {'messages':[HumanMessage(content=user_input)]}, 
        config=CONFIG,
        stream_mode='messages'           
        )
        
        llm_response = st.write_stream(message_chunk.content for message_chunk, metadata in stream_generator)

        st.session_state['message_history'].append({'role':'assistant','content':llm_response})
