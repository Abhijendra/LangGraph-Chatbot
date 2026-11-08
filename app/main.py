import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from app.core.logger import setup_logging
from app.api.routes.chat import router as chat_router
from app.agent.graph import get_graph
from app.db.engine import engine, SessionLocal

# Setup unified logging system immediately on application import
setup_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info(f"HR database connection OK.")
        
        app.state.graph = get_graph()
        yield

    except ConnectionError as e:
        logger.error(f"HR Database connection Error: {e}", exc_info=True)
    
    finally:
        await engine.dispose()

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