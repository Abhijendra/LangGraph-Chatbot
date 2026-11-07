# Chat execution & streaming endpoints

from fastapi import APIRouter

from app.api.schemas import QueryRequest, QueryResponse

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):

    # request.query
    return QueryResponse(response=request.query)
