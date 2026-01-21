"""
pytest 공통 설정 및 Fixture

테스트 DB: .env.test 또는 DATABASE_URL 미설정 시
  postgresql://...@localhost:5434/ddangha_test (docker-compose.yml 의 postgres-test) 사용.
통합 테스트 실행 전에 `docker compose up` 또는 `docker compose up postgres-test -d` 필요.
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# main import 전에 테스트 DB URL 설정 (database.py가 import 시점에 DATABASE_URL 사용)
_test_env = Path(__file__).resolve().parent.parent / ".env.test"
if _test_env.exists():
    load_dotenv(_test_env, override=True)
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://ddangha_user:ddangha_password@localhost:5434/ddangha_test",
)

from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def migrate_test_db():
    """통합 테스트 수집 시 테스트 DB에 마이그레이션 적용 (integration에서만 사용)."""
    from alembic import command
    from alembic.config import Config

    _root = Path(__file__).resolve().parent.parent
    cfg = Config(str(_root / "alembic.ini"))
    command.upgrade(cfg, "head")
    yield


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient Fixture"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """비동기 테스트를 위한 AsyncClient (필요시 사용)"""
    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
