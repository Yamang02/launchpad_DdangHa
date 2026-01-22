"""회원가입 API 통합 테스트 (POST /api/v1/auth/signup)"""

import uuid

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.shared.database import async_session_maker
from app.infrastructure.user.models import UserModel
from main import app

pytestmark = pytest.mark.integration

# DATABASE_URL: conftest에서 postgres-test(5434/ddangha_test)로 설정. docker compose up 또는 test:infra:up 필요.


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
    """테스트 DB(ddangha_test)가 실행 간 유지되므로 이메일을 매번 유니크하게 생성."""
    return {
        "email": f"signup-{uuid.uuid4().hex[:12]}@example.com",
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

    async def test_signup_duplicate_email(self, async_client: AsyncClient):
        """중복 이메일 회원가입 실패 (409)"""
        email = f"dup-{uuid.uuid4().hex[:12]}@example.com"
        payload = {
            "email": email,
            "password": "securePassword123",
            "nickname": "중복테스트",
        }
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
        """응답 형식 검증: uid, email, nickname (이메일은 valid_signup_data의 유니크 값 사용)"""
        payload = valid_signup_data
        response = await async_client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "data" in data
        d = data["data"]
        assert "uid" in d and d["uid"].startswith("usr_")
        assert "email" in d and "nickname" in d

    async def test_signup_persists_to_test_db(self, async_client: AsyncClient):
        """회원가입 시 test DB에 한글 닉네임까지 정확히 저장되는지 검증"""
        email = f"db-check-{uuid.uuid4().hex[:8]}@example.com"
        nickname = "한글닉네임"
        payload = {
            "email": email,
            "password": "securePassword123",
            "nickname": nickname,
        }
        response = await async_client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == status.HTTP_201_CREATED, response.text

        async with async_session_maker() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalar_one_or_none()
        assert user is not None, "test DB에 회원가입 레코드가 있어야 함"
        assert user.email == email
        assert user.nickname == nickname, "한글 닉네임이 test DB에 올바르게 저장되어야 함"
        assert user.uid.startswith("usr_")
