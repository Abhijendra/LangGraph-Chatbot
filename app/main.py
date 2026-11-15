import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from sqlalchemy import text
from app.core.logger import setup_logging
from app.core.config import settings
from app.core.rate_limit import limiter
from app.agent.graph import get_graph
from app.db.engine import engine, SessionLocal
from app.api.routes.chat import router as chat_router
from app.api.routes.auth import router as auth_router

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
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Only the origins listed in BACKEND_CORS_ORIGINS may call this API from a browser.
# Pydantic adds a trailing "/" to URLs, but browsers send origins without it.
cors_origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]

if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"]
    )

app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Users query"]
    )

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Login"]
)


@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Welcome to the central API gateway!"}