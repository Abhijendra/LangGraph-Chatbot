# StateGraph construction & compilation

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import InMemorySaver

from app.agent.state import ChatState
from app.agent.nodes import chat_node
from app.agent.tools import tool_node

def get_graph():
    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)


    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools","chat_node")
    
    chatbot = graph.compile(checkpointer=InMemorySaver())
    return chatbot

if __name__ == "__main__":

    chatbot = get_graph()
    print(chatbot)
