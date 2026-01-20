"""
DB 연결 단위 테스트 (TDD - Phase 1 shared)
spec: 001-signup-design — get_db async generator
"""

import inspect

import pytest

from app.shared.database import get_db


def test_get_db_is_async_generator_function():
    """get_db는 async generator 함수이다."""
    assert inspect.isasyncgenfunction(get_db)


@pytest.mark.asyncio
async def test_get_db_yields_session_once():
    """get_db를 소비하면 한 번 yield하고, 그 값은 AsyncSession처럼 close 가능해야 한다."""
    gen = get_db()
    session = await gen.__anext__()
    # AsyncSession은 close() 메서드를 가진다 (async)
    assert hasattr(session, "close")
    assert callable(getattr(session, "close", None))
    # 제너레이터 종료 (다음 anext 시 StopAsyncIteration)
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()
