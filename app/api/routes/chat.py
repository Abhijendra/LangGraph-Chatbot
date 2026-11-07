# Chat execution & streaming endpoints
import logging 

from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.api.schemas import QueryRequest, QueryResponse
from app.agent.nodes import chat_node

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):

    state = {"messages":[ HumanMessage(content=request.query)]}

    raw_res = await chat_node(state=state)

    # res.content
    res = raw_res["messages"][-1].content
    logger.info(f"Response Content: {res}")
    return QueryResponse(response=res)