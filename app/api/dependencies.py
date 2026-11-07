from fastapi import Request
from langgraph.graph.state import CompiledStateGraph

def get_chatbot(request: Request) -> CompiledStateGraph:
    
    # Every request carries a reference to the app (request.app), 
    # so request.app.state.graph retrieves that same stored graph.
    return request.app.state.graph 