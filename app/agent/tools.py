# Custom agent tools (web search, DB tools)

import logging
import requests

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from app.core.config import settings

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

    # NOTE: requests.get has no timeout and no error handling. Alpha Vantage returns HTTP 200 with a "rate limit" note in the JSON, so the model would get confusing output.
    res = requests.get(url)

    # logger.info(f"HTTP Response status code: {res.status_code}")
    return res.json()


def fetch_db_data():
    """
    Fetch data from postgresql DB.
    """
    pass

tools = [get_stock_price]
tool_node = ToolNode(tools)