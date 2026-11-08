from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

def build_engine():
    
    engine = create_async_engine(
        url=settings.HR_DATABASE_URL.get_secret_value(),
        pool_size=settings.HR_DATABASE_POOL_SIZE,
        pool_pre_ping=True
        )
    
    return engine


engine = build_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)