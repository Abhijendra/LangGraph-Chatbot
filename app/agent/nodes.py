# Node functions (LLM orchestration, logic)

import asyncio
from datetime import datetime

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.agent.state import ChatState
from app.agent.prompts import get_chat_prompt_template
from langchain_core.messages import HumanMessage

model = ChatOpenAI(
    model=settings.DEFAULT_MODEL_NAME,
    temperature=settings.MODEL_TEMPERATURE,
    api_key=settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else None
)

async def chat_node(state: ChatState):
    """
    A LangGraph node that executes the LLM with injected prompts and history.
    """

    prompt_template = get_chat_prompt_template()

    current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    local_prompt = prompt_template.partial(
        current_time = current_time
    )

    llm_chain = local_prompt | model

    messages = state["messages"]

    response = await llm_chain.ainvoke({"messages":messages})
    
    return {"messages": [response]}


if __name__ == "__main__":

    state = {"messages":[HumanMessage(content="Hello, How you doin'?")]}
    res= asyncio.run(chat_node(state))
    print(f"Res:{res}")