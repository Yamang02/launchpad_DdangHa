"""
도메인 예외 단위 테스트 (TDD - Phase 1 shared)
spec: 001-signup-design — DomainError, ValidationError, DuplicateEmailError
"""

import pytest

from app.shared.exceptions import DomainError, DuplicateEmailError, ValidationError


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
