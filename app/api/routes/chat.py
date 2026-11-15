# Chat execution & streaming endpoints
import logging 

from fastapi import APIRouter, Depends, Request
from langchain_core.messages import HumanMessage

from app.api.schemas import QueryRequest, QueryResponse
from app.api.dependencies import get_chatbot, get_current_user
from app.core.callbacks import TraceHandler
from app.core.auth import UserContext
from app.core.rate_limit import limiter

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
@limiter.limit("20/minute")
async def query(request:Request,
                body: QueryRequest, 
                graph = Depends(get_chatbot),
                user:UserContext = Depends(get_current_user)):

    logger.debug(f"Request recieved from the user {user.user_id}: {body.query}")
    
    state = {"messages":[ HumanMessage(content=body.query)]}
    
    thread_id = f"{user.user_id}:{body.session_id}"
    config = {
        "configurable": {
            "thread_id": thread_id, 
            "user_id": user.user_id,
            "role": user.role.value
            },
        "callbacks": [TraceHandler(thread_id)],
        "recursion_limit": 10
    }
    
    raw_res = await graph.ainvoke(state,config=config)

    # res.content
    res = raw_res["messages"][-1].content
    logger.debug(f"Response Content: {res}")
    return QueryResponse(response=res)