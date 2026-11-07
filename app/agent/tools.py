# Custom agent tools (web search, DB tools)

from langgraph.prebuilt import ToolNode, tools_condition

tools = []
tool_node = ToolNode(tools)
