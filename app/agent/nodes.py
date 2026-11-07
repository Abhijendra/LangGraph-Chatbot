# Node functions (LLM orchestration, logic)

from langchain_openai import ChatOpenAI

from app.agent.state import ChatState
from app.core.config import settings

model = ChatOpenAI(
    model=settings.DEFAULT_MODEL_NAME,
    temperature=settings.MODEL_TEMPERATURE,
    api_key=settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else None
)

def chat_node(state: ChatState):

    messages = state["messages"]

    response = model.invoke(messages).content
    # print(response)
    return {"messages": [response]}


if __name__ == "__main__":

    state = {"messages":["Hi"]}
    res= chat_node(state)
    print(f"Res:{res}")