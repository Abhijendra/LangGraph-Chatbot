import secrets
import logging

from fastapi import APIRouter, HTTPException, status, Request

from app.core.config import settings
from app.api.schemas import LoginRequest, TokenResponse
from app.db.repository import get_login_info
from app.core.rbac import role_from_job_title
from app.core.security import create_access_token
from app.core.rate_limit import limiter

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request:Request, body: LoginRequest):
    expected = settings.DEV_LOGIN_PASSWORD
    if expected is None or not secrets.compare_digest(body.password, expected.get_secret_value()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Credentials")

    info = await get_login_info(body.employee_id)
    if info is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Credentials")

    role = role_from_job_title(job_title=info["job_title"])
    logger.info(f"Login OK: employee {info["employee_id"]} -> role {role.value}")
    return TokenResponse(
        access_token=create_access_token(info["employee_id"], role)
    )