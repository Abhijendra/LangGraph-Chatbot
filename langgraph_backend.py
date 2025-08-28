from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from typing_extensions import Literal
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
import operator
from langgraph.graph import add_messages
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],  add_messages] # BaseMessage because it is superclass of HumanMessage, AIMessage, ToolMessage and SystemMessage # add_messages is more optimized that operator.add (reduce method) and is recommended by LangGraph

model = ChatOpenAI(model='gpt-4o-mini')

def chat_node(state:ChatState):

    # take user query from state
    messages = state['messages']
    
    # send to llm 
    response = model.invoke(messages).content 

    # store the response in state
    return {'messages':[response]}

checkpointer = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node('chat_node',chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

# stream_generator = chatbot.stream(
#     {'messages':[HumanMessage(content='How to catch a pokemon in pokemon world')]}, 
#     config={'configurable': {'thread_id':'1'}},
#     stream_mode='messages'           
#     )

    # print(type(stream_generator)) # stream_generator is a generator object

    # for message_chunk, metadata in stream_generator:
    #     if message_chunk.content:
    #         print(message_chunk.content, end=' ', flush=True)
