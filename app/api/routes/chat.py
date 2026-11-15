# Chat execution & streaming endpoints
import logging 

from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage

from app.api.schemas import QueryRequest, QueryResponse
from app.api.dependencies import get_chatbot, get_current_user
from app.core.callbacks import TraceHandler
from app.core.auth import UserContext

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, 
                graph = Depends(get_chatbot),
                user:UserContext = Depends(get_current_user)):

    logger.info(f"Request recieved from the user {user.user_id}: {request.query}")
    
    state = {"messages":[ HumanMessage(content=request.query)]}
    
    thread_id = f"{user.user_id}:{request.session_id}"
    config = {
        "configurable": {"thread_id": thread_id, 
                         "user_id": user.user_id,
                         "role": user.role.value,
                         "recursion_limit": 10},
        "callbacks": [TraceHandler(thread_id)]
    }
    
    raw_res = await graph.ainvoke(state,config=config)

    # res.content
    res = raw_res["messages"][-1].content
    logger.info(f"Response Content: {res}")
    return QueryResponse(response=res)