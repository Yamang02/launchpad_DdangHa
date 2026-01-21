"""
AuthService.login() 단위 테스트 (TDD - Phase 2)
spec: 002-login-design — 로그인 서비스 로직
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.auth.application.dtos import LoginRequest, LoginResponse
from app.auth.application.services import AuthService
from app.shared.exceptions import (
    InvalidCredentialsError,
    InactiveAccountError,
    SuspendedAccountError,
)
from app.user.domain.entities import User, UserStatus
from app.shared.security import hash_password


@pytest.fixture
def mock_user_repository():
    """Mock UserRepository"""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_repository):
    """AuthService 인스턴스"""
    return AuthService(mock_user_repository)


@pytest.fixture
def active_user():
    """활성 사용자 엔티티"""
    return User(
        uid="usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
        email="user@example.com",
        password_hash=hash_password("correctPassword123"),
        nickname="테스트유저",
        status=UserStatus.ACTIVE,
    )


@pytest.fixture
def inactive_user():
    """비활성 사용자 엔티티"""
    return User(
        uid="usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
        email="user@example.com",
        password_hash=hash_password("correctPassword123"),
        nickname="테스트유저",
        status=UserStatus.INACTIVE,
    )


@pytest.fixture
def suspended_user():
    """정지된 사용자 엔티티"""
    return User(
        uid="usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
        email="user@example.com",
        password_hash=hash_password("correctPassword123"),
        nickname="테스트유저",
        status=UserStatus.SUSPENDED,
    )


@pytest.mark.asyncio
async def test_login_success(auth_service, mock_user_repository, active_user):
    """유효한 자격증명으로 로그인 성공"""
    mock_user_repository.get_by_email.return_value = active_user
    mock_user_repository.update_last_login = AsyncMock()

    request = LoginRequest(email="user@example.com", password="correctPassword123")
    response = await auth_service.login(request)

    assert isinstance(response, LoginResponse)
    assert response.access_token is not None
    assert response.refresh_token is not None
    assert response.token_type == "Bearer"
    assert response.expires_in == 900  # 15분 = 900초

    mock_user_repository.get_by_email.assert_called_once_with("user@example.com")
    mock_user_repository.update_last_login.assert_called_once_with(active_user.uid)


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, mock_user_repository):
    """존재하지 않는 이메일로 로그인 실패"""
    mock_user_repository.get_by_email.return_value = None

    request = LoginRequest(email="nonexistent@example.com", password="anyPassword")
    
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(request)

    mock_user_repository.get_by_email.assert_called_once_with("nonexistent@example.com")
    mock_user_repository.update_last_login.assert_not_called()


@pytest.mark.asyncio
async def test_login_invalid_password(auth_service, mock_user_repository, active_user):
    """잘못된 비밀번호로 로그인 실패"""
    mock_user_repository.get_by_email.return_value = active_user

    request = LoginRequest(email="user@example.com", password="wrongPassword")
    
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(request)

    mock_user_repository.get_by_email.assert_called_once_with("user@example.com")
    mock_user_repository.update_last_login.assert_not_called()


@pytest.mark.asyncio
async def test_login_inactive_account(auth_service, mock_user_repository, inactive_user):
    """비활성화된 계정 로그인 실패"""
    mock_user_repository.get_by_email.return_value = inactive_user

    request = LoginRequest(email="user@example.com", password="correctPassword123")
    
    with pytest.raises(InactiveAccountError):
        await auth_service.login(request)

    mock_user_repository.get_by_email.assert_called_once_with("user@example.com")
    mock_user_repository.update_last_login.assert_not_called()


@pytest.mark.asyncio
async def test_login_suspended_account(auth_service, mock_user_repository, suspended_user):
    """정지된 계정 로그인 실패"""
    mock_user_repository.get_by_email.return_value = suspended_user

    request = LoginRequest(email="user@example.com", password="correctPassword123")
    
    with pytest.raises(SuspendedAccountError):
        await auth_service.login(request)

    mock_user_repository.get_by_email.assert_called_once_with("user@example.com")
    mock_user_repository.update_last_login.assert_not_called()


@pytest.mark.asyncio
async def test_login_updates_last_login_at(auth_service, mock_user_repository, active_user):
    """로그인 성공 시 last_login_at 업데이트"""
    mock_user_repository.get_by_email.return_value = active_user
    mock_user_repository.update_last_login = AsyncMock()

    request = LoginRequest(email="user@example.com", password="correctPassword123")
    await auth_service.login(request)

    mock_user_repository.update_last_login.assert_called_once_with(active_user.uid)


@pytest.mark.asyncio
async def test_login_returns_valid_tokens(auth_service, mock_user_repository, active_user):
    """로그인 성공 시 유효한 Access Token 및 Refresh Token 반환"""
    from app.auth.infrastructure.jwt_handler import verify_token, get_token_uid
    
    mock_user_repository.get_by_email.return_value = active_user
    mock_user_repository.update_last_login = AsyncMock()

    request = LoginRequest(email="user@example.com", password="correctPassword123")
    response = await auth_service.login(request)

    # Access Token 검증
    access_payload = verify_token(response.access_token)
    assert access_payload is not None
    assert access_payload.get("type") == "access"
    assert get_token_uid(access_payload) == active_user.uid

    # Refresh Token 검증
    refresh_payload = verify_token(response.refresh_token)
    assert refresh_payload is not None
    assert refresh_payload.get("type") == "refresh"
    assert get_token_uid(refresh_payload) == active_user.uid
