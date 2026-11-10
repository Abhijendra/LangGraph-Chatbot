# Chat execution & streaming endpoints
import logging 

from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage

from app.api.schemas import QueryRequest, QueryResponse
from app.api.dependencies import get_chatbot
from app.core.callbacks import TraceHandler
router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, graph = Depends(get_chatbot)):

    logger.info(f"Request recieved from the user: {request.query}")
    
    state = {"messages":[ HumanMessage(content=request.query)]}
    
    thread_id = f"{request.userid}:{request.session_id}"
    config = {
        "configurable": {"thread_id": thread_id, 
                         "user_id": "AVG002",
                         "role": "CTO"},
        "callbacks": [TraceHandler(thread_id)]
    }
    
    raw_res = await graph.ainvoke(state,config=config)

    # res.content
    res = raw_res["messages"][-1].content
    logger.info(f"Response Content: {res}")
    return QueryResponse(response=res)