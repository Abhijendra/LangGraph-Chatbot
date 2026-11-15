import logging
import requests

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.core.config import settings
from app.agent.tools.utils import get_user_context
from app.core.rbac import require, Permission, PermissionDenied

logger = logging.getLogger(__name__)

@tool
def get_stock_price(config:RunnableConfig, symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL'
    , 'TSLA') using Alpha Vantage with API key in the URL.
    """

    user = get_user_context(config)
    try:
        require(user, Permission.FINANCE_READ)
    except PermissionDenied as e:
        return str(e)

    # logger.info(f"Stock Prices tool called with argument: Symbol={symbol}")
    base_url = "https://www.alphavantage.co"
    api_key = settings.ALPHA_VANTAGE_API_KEY.get_secret_value()
    url = f"{base_url}/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

    # NOTE: requests.get has no timeout and no error handling. 
    # Alpha Vantage returns HTTP 200 with a "rate limit" note in the 
    # JSON, so the model would get confusing output.
    res = requests.get(url)

    return res.json()

finance_tools = [get_stock_price]