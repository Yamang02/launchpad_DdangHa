"""
API 표준 응답 형식 통합 테스트
spec: 000-foundation — success/data, success/error
"""
import pytest

from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_spec_ok_returns_200_with_success_and_data(client: TestClient):
    """GET /api/v1/_spec/ok → 200, success=True, data 존재"""
    response = client.get("/api/v1/_spec/ok")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert isinstance(data["data"], dict)


def test_spec_error_returns_400_with_success_false_and_error(client: TestClient):
    """GET /api/v1/_spec/error → 400, success=False, error.code, error.message"""
    response = client.get("/api/v1/_spec/error")
    assert response.status_code == 400
    body = response.json()
    assert body.get("success") is False
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]
