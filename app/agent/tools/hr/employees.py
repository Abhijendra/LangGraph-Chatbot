import logging

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import UserContext
from app.db.repository import get_by_name

logger = logging.getLogger(__name__)

@tool
async def get_employees_by_name(config: RunnableConfig, 
                                first_name:str, 
                                last_name:str|None=None) -> str | list[dict]:
    """
    Fetch employees details (employee_id, first_name, last_name,
    department_id) using first name and/or last name where first_name 
    is mandatory. Returns at most 5 matches.

    Arguments:
    first_name: First name of the employee. (Mandatory)
    last_name: last name of the employee.
    """
    user_id = config.get("configurable", {}).get("user_id")
    role = config.get("configurable", {}).get("role")

    logger.info(f"Tool call by LLM done for User id : {user_id} | Role: {role}")

    if user_id is None or role is None:
        raise ValueError("User not found.")
    
    user = UserContext(user_id, role)
    try:
        employees = await get_by_name(user, name=first_name, last_name=last_name)
    except SQLAlchemyError:
        logger.exception("SQLAlchemy error.")
        return "The employee database is unavailable right now. Please try again later."
    except OSError:
        logger.exception("DB connection issue.")
        return "The employee database is unavailable right now. Please try again later."

    if not len(employees):
        return "No employees found."

    logger.info(f"No. of rows returned : {len(employees)}")
    return employees


hr_tools = [get_employees_by_name]