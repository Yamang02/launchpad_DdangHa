"""
pytest 공통 설정 및 Fixture
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient Fixture"""
    return TestClient(app)


@pytest.fixture
def async_client():
    """비동기 테스트를 위한 AsyncClient (필요시 사용)"""
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
