from langgraph.prebuilt import ToolNode

from app.agent.tools.finance.stocks import finance_tools
from app.agent.tools.hr.employees import hr_tools

tools = [*finance_tools, *hr_tools]  # `*` unpacks each list into the new one

tool_node = ToolNode(tools)