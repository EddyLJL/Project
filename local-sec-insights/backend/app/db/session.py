from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/llama_app_db"

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

# 保留旧的命名以兼容现有代码
SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 新的异步会话管理方式
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
