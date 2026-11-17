# StateGraph construction & compilation

from langgraph.graph import StateGraph, END, START

from app.agent.state import ChatState
from app.agent.nodes import chat_node
from app.agent.tools.registry import guarded_tool_node
from app.agent.summarizer import summarize_node, route_after_chat

def get_graph(checkpointer):
    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", guarded_tool_node)
    graph.add_node("summarize", summarize_node)


    graph.add_edge(START, "chat_node")
    # graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_conditional_edges("chat_node", route_after_chat, ["tools", "summarize", END])
    graph.add_edge("tools","chat_node")
    graph.add_edge("summarize", END)

    
    chatbot = graph.compile(checkpointer=checkpointer)
    return chatbot