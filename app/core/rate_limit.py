from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

def user_or_ip_key(request:Request) -> str:
    # get_current_user sets request.state.user_id; fall back to IP (e.g. login)
    return getattr(request.state, "user_id", None) or get_remote_address(request)

limiter = Limiter(key_func=user_or_ip_key)