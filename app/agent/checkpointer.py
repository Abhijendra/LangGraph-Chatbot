from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings, BASE_DIR

@asynccontextmanager
async def make_checkpointer():

    kind = settings.CHECKPOINTER_TYPE

    if kind == "memory":
        from langgraph.checkpoint.memory import InMemorySaver
        yield InMemorySaver()

    elif kind == "sqlite":
        
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        path = BASE_DIR / Path(settings.CHECKPOINTER_SQLITE_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        async with AsyncSqliteSaver.from_conn_string(str(path)) as saver:
            yield saver

    elif kind == "postgres":

        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        if  settings.CHECKPOINTER_POSTGRES_URL is None:
            raise ValueError("Postgres checkpointer url is empty.")
        postgres_checkpointer_dsn = settings.CHECKPOINTER_POSTGRES_URL.get_secret_value()
        async with AsyncPostgresSaver.from_conn_string(postgres_checkpointer_dsn) as saver:
            await saver.setup()
            yield saver

    else:

        raise ValueError(f"Unknown Checkpointer Type: {kind}")