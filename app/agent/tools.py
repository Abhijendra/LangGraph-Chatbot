# Custom agent tools (web search, DB tools)

import logging
import requests

from sqlalchemy.exc import SQLAlchemyError

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolNode

from app.core.config import settings
from app.core.auth import UserContext
from app.db.repository import get_by_name


logger = logging.getLogger(__name__)

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL'
    , 'TSLA') using Alpha Vantage with API key in the URL.
    """
    # logger.info(f"Stock Prices tool called with argument: Symbol={symbol}")
    base_url = "https://www.alphavantage.co"
    api_key = settings.ALPHA_VANTAGE_API_KEY.get_secret_value()
    url = f"{base_url}/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

    # NOTE: requests.get has no timeout and no error handling. 
    # Alpha Vantage returns HTTP 200 with a "rate limit" note in the 
    # JSON, so the model would get confusing output.
    res = requests.get(url)

    # logger.info(f"HTTP Response status code: {res.status_code}")
    return res.json()

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

tools = [get_stock_price, get_employees_by_name]
tool_node = ToolNode(tools)