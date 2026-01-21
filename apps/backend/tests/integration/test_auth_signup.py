"""회원가입 API 통합 테스트 (POST /api/v1/auth/signup)"""

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app

# DATABASE_URL 필요 (로컬: postgres, docker: postgres 서비스). DB 없으면 스킵 가능.


@pytest.fixture
async def async_client():
    """AsyncClient 픽스처 (ASGI)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def valid_signup_data():
    return {
        "email": "test-signup@example.com",
        "password": "securePassword123",
        "nickname": "테스트유저",
    }


class TestSignup:
    """회원가입 API 통합 테스트"""

    async def test_signup_success(
        self, async_client: AsyncClient, valid_signup_data: dict
    ):
        """유효한 정보로 회원가입 성공 (201)"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json=valid_signup_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        assert "uid" in data["data"]
        assert data["data"]["uid"].startswith("usr_")
        assert data["data"]["email"] == valid_signup_data["email"]
        assert data["data"]["nickname"] == valid_signup_data["nickname"]

    async def test_signup_duplicate_email(
        self, async_client: AsyncClient, valid_signup_data: dict
    ):
        """중복 이메일 회원가입 실패 (409)"""
        email = "dup-signup@example.com"
        payload = {**valid_signup_data, "email": email}
        await async_client.post("/api/v1/auth/signup", json=payload)
        response = await async_client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT
        body = response.json()
        assert body.get("success") is False
        assert body.get("error", {}).get("code") == "EMAIL_ALREADY_EXISTS"

    async def test_signup_invalid_email_format(self, async_client: AsyncClient):
        """잘못된 이메일 형식 거부 (422)"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "invalid-email",
                "password": "securePassword123",
                "nickname": "테스트",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_short_password(self, async_client: AsyncClient):
        """8자 미만 비밀번호 거부 (422)"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "short1",
                "nickname": "테스트",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_password_without_letter(self, async_client: AsyncClient):
        """영문 미포함 비밀번호 거부 (422)"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "12345678",
                "nickname": "테스트",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_password_without_number(self, async_client: AsyncClient):
        """숫자 미포함 비밀번호 거부 (422)"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "passwordonly",
                "nickname": "테스트",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_short_nickname(self, async_client: AsyncClient):
        """2자 미만 닉네임 거부 (422)"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "securePassword123",
                "nickname": "A",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_long_nickname(self, async_client: AsyncClient):
        """20자 초과 닉네임 거부 (422)"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "securePassword123",
                "nickname": "A" * 21,
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_response_format(
        self, async_client: AsyncClient, valid_signup_data: dict
    ):
        """응답 형식 검증: uid, email, nickname"""
        payload = {**valid_signup_data, "email": "format-check@example.com"}
        response = await async_client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "data" in data
        d = data["data"]
        assert "uid" in d and d["uid"].startswith("usr_")
        assert "email" in d and "nickname" in d
