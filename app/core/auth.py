from enum import Enum
from dataclasses import dataclass

class Role(str, Enum):
    EMPLOYEE = "employee"
    HR = "hr"
    ADMIN = "admin"

@dataclass(frozen=True)
class UserContext:
    user_id: str
    role: Role