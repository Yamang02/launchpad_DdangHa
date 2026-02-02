"""
도메인 예외 단위 테스트 (TDD - Phase 1 shared, Phase 4 login)
spec: 001-signup-design — DomainError, ValidationError, DuplicateEmailError
spec: 002-login-design — InvalidCredentialsError, InactiveAccountError, SuspendedAccountError
"""

import pytest

from app.shared.exceptions import (
    DomainError,
    DuplicateEmailError,
    ValidationError,
    InvalidCredentialsError,
    InactiveAccountError,
    SuspendedAccountError,
)


def test_domain_error_has_message_and_code():
    """DomainError는 message와 code를 갖는다."""
    e = DomainError("테스트 메시지", code="TEST_CODE")
    assert e.message == "테스트 메시지"
    assert e.code == "TEST_CODE"
    assert str(e) == "테스트 메시지"


def test_domain_error_default_code():
    """DomainError의 기본 code는 DOMAIN_ERROR이다."""
    e = DomainError("msg")
    assert e.code == "DOMAIN_ERROR"


def test_validation_error_inherits_domain_error():
    """ValidationError는 DomainError를 상속하고 code는 VALIDATION_ERROR이다."""
    e = ValidationError("필드 오류", field="email")
    assert isinstance(e, DomainError)
    assert e.code == "VALIDATION_ERROR"
    assert e.message == "필드 오류"
    assert e.field == "email"


def test_validation_error_field_optional():
    """ValidationError의 field는 None일 수 있다."""
    e = ValidationError("일반 오류")
    assert e.field is None


def test_duplicate_email_error_message_and_email():
    """DuplicateEmailError는 이메일 중복 메시지와 email 속성을 갖는다."""
    e = DuplicateEmailError("dup@example.com")
    assert e.code == "EMAIL_ALREADY_EXISTS"
    assert "이미 사용 중인 이메일" in e.message
    assert "dup@example.com" in e.message
    assert e.email == "dup@example.com"


def test_invalid_credentials_error_inherits_domain_error():
    """InvalidCredentialsError는 DomainError를 상속하고 code는 INVALID_CREDENTIALS이다."""
    e = InvalidCredentialsError()
    assert isinstance(e, DomainError)
    assert e.code == "INVALID_CREDENTIALS"
    assert e.message == "이메일 또는 비밀번호가 올바르지 않습니다."


def test_inactive_account_error_inherits_domain_error():
    """InactiveAccountError는 DomainError를 상속하고 code는 ACCOUNT_INACTIVE이다."""
    e = InactiveAccountError()
    assert isinstance(e, DomainError)
    assert e.code == "ACCOUNT_INACTIVE"
    assert e.message == "비활성화된 계정입니다. 고객센터로 문의해주세요."


def test_suspended_account_error_inherits_domain_error():
    """SuspendedAccountError는 DomainError를 상속하고 code는 ACCOUNT_SUSPENDED이다."""
    e = SuspendedAccountError()
    assert isinstance(e, DomainError)
    assert e.code == "ACCOUNT_SUSPENDED"
    assert e.message == "정지된 계정입니다. 고객센터로 문의해주세요."
