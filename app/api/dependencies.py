import jwt

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from langgraph.graph.state import CompiledStateGraph

from  app.core.auth import UserContext, Role
from app.core.security import decode_access_token


def get_chatbot(request: Request) -> CompiledStateGraph:
    
    # Every request carries a reference to the app (request.app), 
    # so request.app.state.graph retrieves that same stored graph.
    return request.app.state.graph 

bearer_scheme = HTTPBearer() # also adds the "Authorize" button in /docs

def get_current_user(
        request:Request,
        creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ) -> UserContext:
    try:
        payload = decode_access_token(creds.credentials)
        user = UserContext(
            user_id=payload["sub"],
            role= Role(payload["role"])
        )
        request.state.user_id = user.user_id
        return user
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired Token", headers={"WWW-Authenticate": "Bearer"})