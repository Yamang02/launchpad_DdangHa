"""Auth DTO 유효성 검증 단위 테스트"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.auth.application.dtos import SignupRequest, LoginRequest, LoginResponse


def test_signup_request_valid():
    """유효한 요청 통과"""
    req = SignupRequest(
        email="user@example.com",
        password="securePass1",
        nickname="홍길동",
    )
    assert req.email == "user@example.com"
    assert req.password == "securePass1"
    assert req.nickname == "홍길동"


def test_signup_request_invalid_email():
    """잘못된 이메일 형식 거부"""
    with pytest.raises(PydanticValidationError) as exc_info:
        SignupRequest(
            email="invalid-email",
            password="securePass1",
            nickname="테스트",
        )
    errors = exc_info.value.errors()
    assert any("email" in str(e.get("loc", [])) for e in errors)


def test_signup_request_short_password():
    """8자 미만 비밀번호 거부"""
    with pytest.raises(PydanticValidationError) as exc_info:
        SignupRequest(
            email="user@example.com",
            password="short1",
            nickname="테스트",
        )
    errors = exc_info.value.errors()
    assert any("password" in str(e.get("loc", [])) for e in errors)


def test_signup_request_password_without_letter():
    """영문 미포함 비밀번호 거부"""
    with pytest.raises(PydanticValidationError) as exc_info:
        SignupRequest(
            email="user@example.com",
            password="12345678",
            nickname="테스트",
        )
    errors = exc_info.value.errors()
    assert any("password" in str(e.get("loc", [])) for e in errors)


def test_signup_request_password_without_number():
    """숫자 미포함 비밀번호 거부"""
    with pytest.raises(PydanticValidationError) as exc_info:
        SignupRequest(
            email="user@example.com",
            password="passwordonly",
            nickname="테스트",
        )
    errors = exc_info.value.errors()
    assert any("password" in str(e.get("loc", [])) for e in errors)


def test_signup_request_short_nickname():
    """2자 미만 닉네임 거부"""
    with pytest.raises(PydanticValidationError) as exc_info:
        SignupRequest(
            email="user@example.com",
            password="securePass1",
            nickname="A",
        )
    errors = exc_info.value.errors()
    assert any("nickname" in str(e.get("loc", [])) for e in errors)


def test_signup_request_long_nickname():
    """20자 초과 닉네임 거부"""
    with pytest.raises(PydanticValidationError) as exc_info:
        SignupRequest(
            email="user@example.com",
            password="securePass1",
            nickname="A" * 21,
        )
    errors = exc_info.value.errors()
    assert any("nickname" in str(e.get("loc", [])) for e in errors)


# LoginRequest 테스트
def test_login_request_valid():
    """유효한 로그인 요청 통과"""
    req = LoginRequest(
        email="user@example.com",
        password="anyPassword123",
    )
    assert req.email == "user@example.com"
    assert req.password == "anyPassword123"


def test_login_request_invalid_email():
    """잘못된 이메일 형식 거부"""
    with pytest.raises(PydanticValidationError) as exc_info:
        LoginRequest(
            email="invalid-email",
            password="anyPassword123",
        )
    errors = exc_info.value.errors()
    assert any("email" in str(e.get("loc", [])) for e in errors)


def test_login_request_empty_password():
    """빈 비밀번호 거부"""
    with pytest.raises(PydanticValidationError) as exc_info:
        LoginRequest(
            email="user@example.com",
            password="",
        )
    errors = exc_info.value.errors()
    assert any("password" in str(e.get("loc", [])) for e in errors)


# LoginResponse 테스트
def test_login_response_valid():
    """유효한 로그인 응답 생성"""
    response = LoginResponse(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        refresh_token="rtk_01ARZ3NDEKTSV4RRFFQ69G5FAV",
        token_type="Bearer",
        expires_in=900,
    )
    assert response.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    assert response.refresh_token == "rtk_01ARZ3NDEKTSV4RRFFQ69G5FAV"
    assert response.token_type == "Bearer"
    assert response.expires_in == 900


def test_login_response_default_token_type():
    """LoginResponse의 기본 token_type은 'Bearer'"""
    response = LoginResponse(
        access_token="token",
        refresh_token="refresh",
        expires_in=900,
    )
    assert response.token_type == "Bearer"
