"""
UID 생성 유틸리티 테스트 (TDD RED)
spec: 000-foundation
"""
import re

import pytest

from app.shared.uid import generate_uid, generate_user_uid

# ULID 26자: Crockford Base32 [0-9A-HJKMNP-TV-Z] (I,L,O,U 제외)
ULID_PATTERN = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")


class TestGenerateUid:
    """generate_uid(prefix)"""

    def test_returns_string_with_prefix_and_ulid(self):
        """prefix + ULID 26자 형식이어야 함"""
        result = generate_uid("usr_")
        assert isinstance(result, str)
        assert result.startswith("usr_")
        assert ULID_PATTERN.fullmatch(result[4:]) is not None

    def test_prefix_is_preserved(self):
        """다양한 prefix가 그대로 붙어야 함"""
        for prefix in ("usr_", "rtk_", "x_"):
            result = generate_uid(prefix)
            assert result.startswith(prefix)
            assert result[ len(prefix) : ] != ""

    def test_each_call_produces_different_value(self):
        """호출마다 서로 다른 값 생성"""
        a = generate_uid("t_")
        b = generate_uid("t_")
        assert a != b


class TestGenerateUserUid:
    """generate_user_uid()"""

    def test_returns_usr_prefix(self):
        """usr_ prefix가 붙어야 함"""
        result = generate_user_uid()
        assert result.startswith("usr_")

    def test_has_ulid_after_prefix(self):
        """usr_ 뒤 26자가 ULID 형식이어야 함"""
        result = generate_user_uid()
        assert len(result) == 4 + 26
        assert ULID_PATTERN.fullmatch(result[4:]) is not None
