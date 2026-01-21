"""SignupRequest DTO 유효성 검증 단위 테스트"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.auth.application.dtos import SignupRequest


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
