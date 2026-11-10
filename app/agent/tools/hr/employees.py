import logging

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import UserContext
from app.db.repository import get_by_name, get_department_by_id

logger = logging.getLogger(__name__)

DB_UNAVAILABLE_MSG = "The employee database is unavailable right now. Please try again later."

def get_user_context(config:RunnableConfig):
    user_id = config.get("configurable", {}).get("user_id")
    role = config.get("configurable", {}).get("role")

    logger.info(f"Tool call by LLM done for User id : {user_id} | Role: {role}")

    if user_id is None or role is None:
        raise ValueError("User not found.")
    
    return UserContext(user_id, role)

async def run_query(query_fn, *args, not_found:str, **kwargs) -> str | list[dict]:

    try:
        rows = await query_fn(*args, **kwargs)

    except (SQLAlchemyError, OSError):
        logger.exception("Database Error in %s", query_fn.__name__)
        return DB_UNAVAILABLE_MSG

    if not rows:
        return not_found

    logger.info(f"No. of row  returned: {len(rows)}")
    return rows

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
    user = get_user_context(config)
    employees = await run_query(get_by_name, user, name=first_name, last_name=last_name, not_found="No employees found.")
    return employees

@tool
async def get_department_details_by_id(config:RunnableConfig,
                         department_id:int) -> str|list[dict]:
    """
    Fetches all the detail of department by department id.

    Arguments: 
    1. department_id:int
    """
    user = get_user_context(config)
    depts = await run_query(get_department_by_id, user, department_id, not_found="No department found.")
    return depts

hr_tools = [get_employees_by_name, get_department_details_by_id]