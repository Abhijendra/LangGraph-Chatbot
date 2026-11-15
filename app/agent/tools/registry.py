import logging

from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage

from app.core.rbac import Permission, Role, ROLE_PERMISSIONS

from app.agent.tools.finance.stocks import finance_tools
from app.agent.tools.hr.employees import hr_tools

logger = logging.getLogger(__name__)

tools = [*finance_tools, *hr_tools]  # `*` unpacks each list into the new one
tool_node = ToolNode(tools)

TOOL_REQUIRES = {
    "get_employees_by_name": Permission.EMPLOYEE_READ_BASIC,
    "get_department_details_by_id": Permission.DEPARTMENT_READ,
    "get_employee_details_by_id": Permission.EMPLOYEE_READ_OWN_DETAILS,
    "get_stock_price": Permission.FINANCE_READ
}

missing = {t.name for t in tools} - TOOL_REQUIRES.keys()
if missing:
    raise RuntimeError(f"Missing tools in TOOL_REQUIRES: {missing}")

def tools_for(role:Role):
    allowed = ROLE_PERMISSIONS[role]
    return [t for t in tools if TOOL_REQUIRES.get(t.name) in allowed]

async def guarded_tool_node(state, config):

    role:Role = Role(config["configurable"]["role"])
    allowed = {t.name for t in tools_for(role)}
    last = state["messages"][-1]

    blocked = [c for c in last.tool_calls if c["name"] not in allowed]

    if not blocked:
        return await tool_node.ainvoke(state, config)

    # 1. a "no permission" reply for each blocked call
    replies = [
            ToolMessage(
                content="You do not have permission to use this tool.", 
                tool_call_id=c["id"],
                name=c["name"]
            ) for c in blocked
        ]

    logger.warning("BLOCKED tool call: user=%s role=%s tools=%s",
               config["configurable"]["user_id"], role.value,
               [c["name"] for c in blocked])
    
    # 2. run only the allowed calls through the normal tool node
    ok_calls = [c for c in last.tool_calls if c["name"] in allowed]

    if ok_calls:
        ok_msg = last.model_copy(update={"tool_calls": ok_calls})
        result = await tool_node.ainvoke({"messages": [ok_msg]}, config)
        replies += result["messages"]

    return {"messages": replies}

    