"""DB 연결 설정"""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool


class Base(DeclarativeBase):
    """SQLAlchemy ORM Declarative Base"""

    pass

# postgresql:// -> postgresql+asyncpg:// (async SQLAlchemy)
_url = os.getenv("DATABASE_URL", "").strip()
if not _url:
    _url = "postgresql+asyncpg://localhost:5432/ddangha_db"
elif _url.startswith("postgresql://") and "asyncpg" not in _url:
    _url = _url.replace("postgresql://", "postgresql+asyncpg://", 1)

# 테스트용 DB(ddangha_test) 사용 시 NullPool: 연결 재사용 없이 테스트 간 격리, asyncpg "another operation is in progress" 완화
_engine_kw: dict = {"echo": os.getenv("SQL_ECHO", "").lower() in ("1", "true")}
if "ddangha_test" in (_url or ""):
    _engine_kw["poolclass"] = NullPool

engine = create_async_engine(_url, **_engine_kw)
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
