"""
비밀번호 해싱/검증 단위 테스트 (TDD - Phase 1 shared)
spec: 001-signup-design — hash_password, verify_password
"""

import pytest

from app.shared.security import hash_password, verify_password


def test_hash_password_returns_non_empty_bcrypt_like_string():
    """hash_password는 bcrypt 형태의 비밀번호 해시를 반환한다."""
    result = hash_password("mySecret123")
    assert isinstance(result, str)
    assert len(result) > 0
    # bcrypt 해시는 $2b$ 또는 $2a$로 시작
    assert result.startswith("$2")


def test_hash_password_different_for_same_input_due_to_salt():
    """같은 입력이라도 salt 때문에 매번 다른 해시가 생성된다."""
    r1 = hash_password("samePassword")
    r2 = hash_password("samePassword")
    assert r1 != r2


def test_verify_password_returns_true_for_correct_password():
    """올바른 평문 비밀번호와 해시를 주면 True를 반환한다."""
    hashed = hash_password("correctPassword")
    assert verify_password("correctPassword", hashed) is True


def test_verify_password_returns_false_for_wrong_password():
    """잘못된 평문 비밀번호를 주면 False를 반환한다."""
    hashed = hash_password("correctPassword")
    assert verify_password("wrongPassword", hashed) is False


def test_verify_password_returns_false_for_empty_plain():
    """빈 평문을 주면 False를 반환한다."""
    hashed = hash_password("any")
    assert verify_password("", hashed) is False
