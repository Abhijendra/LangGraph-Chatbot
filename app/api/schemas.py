from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):

    userid: str = Field(..., min_length=1, max_length=10)
    username: str | None = Field(default=None) 
    query: str = Field(..., min_length=1, max_length=4000)

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v:str) -> str:

        v = v.strip()
        if not v:
            raise ValueError("query must not be blank.")
        return v


class QueryResponse(BaseModel):
    response: str