from langchain_core.runnables import RunnableConfig

from app.core.auth import UserContext
from app.core.rbac import Role

def get_user_context(config:RunnableConfig):
    user_id = config.get("configurable", {}).get("user_id")
    role = config.get("configurable", {}).get("role")

    if user_id is None or role is None:
        raise ValueError("User not found.")
    
    return UserContext(user_id, Role(role))
