"""
메인 애플리케이션 테스트
TDD 연습을 위한 기본 테스트 예제
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """루트 엔드포인트가 정상적으로 응답해야 함"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "DdangHa API is running"
    assert data["status"] == "ok"


def test_health_endpoint(client: TestClient):
    """헬스 체크 엔드포인트가 정상적으로 응답해야 함"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_cors_headers(client: TestClient):
    """CORS 헤더가 올바르게 설정되어 있어야 함"""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    
    # OPTIONS 요청은 200 또는 204를 반환할 수 있음
    assert response.status_code in [200, 204]
