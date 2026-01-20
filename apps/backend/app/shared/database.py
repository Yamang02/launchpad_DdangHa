"""DB 연결 설정"""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# postgresql:// -> postgresql+asyncpg:// (async SQLAlchemy)
_url = os.getenv("DATABASE_URL", "").strip()
if not _url:
    _url = "postgresql+asyncpg://localhost:5432/ddangha_db"
elif _url.startswith("postgresql://") and "asyncpg" not in _url:
    _url = _url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(_url, echo=os.getenv("SQL_ECHO", "").lower() in ("1", "true"))
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends용 DB 세션 제너레이터"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
