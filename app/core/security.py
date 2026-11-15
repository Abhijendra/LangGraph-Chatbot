from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.auth import Role


def create_access_token(employee_id:str, role:Role) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    payload = {
        "sub": str(employee_id), # "sub" (subject) = who this token is for
        "role": role.value,
        "exp": expire  # PyJWT checks this automatically when decoding
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token:str) -> dict:
    """Raises jwt.InvalidTokenError (includes expired tokens) if the token is bad."""
    return jwt.decode(
        token,
        key=settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM]
    )

