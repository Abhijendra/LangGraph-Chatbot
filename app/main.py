from fastapi import FastAPI
from app.core.logger import setup_logging
from app.api.routes.chat import router as chat_router

# Setup unified logging system immediately on application import
setup_logging()

app = FastAPI()

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