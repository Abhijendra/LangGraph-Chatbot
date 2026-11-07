from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.core.logger import setup_logging
from app.api.routes.chat import router as chat_router
from app.agent.graph import get_graph

# Setup unified logging system immediately on application import
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.graph = get_graph()
    yield {
    }


app = FastAPI(lifespan=lifespan)

app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Users query"]
    )


@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Welcome to the central API gateway!"}