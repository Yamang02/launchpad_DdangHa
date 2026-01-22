"""
User 도메인 엔티티 단위 테스트
spec: 001-signup-design — UserStatus, User dataclass
"""
import dataclasses
from datetime import datetime

from app.domain.user.entities import User, UserStatus


class TestUserStatus:
    """UserStatus Enum"""

    def test_has_active_inactive_suspended(self):
        """ACTIVE, INACTIVE, SUSPENDED 값을 갖는다."""
        assert UserStatus.ACTIVE == "active"
        assert UserStatus.INACTIVE == "inactive"
        assert UserStatus.SUSPENDED == "suspended"

    def test_is_string_enum(self):
        """str Enum이므로 값이 문자열이다."""
        assert isinstance(UserStatus.ACTIVE.value, str)
        assert UserStatus.ACTIVE.value == "active"


class TestUser:
    """User dataclass"""

    def test_create_with_required_fields(self):
        """uid, email, password_hash, nickname으로 생성 가능하다."""
        user = User(
            uid="usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
            email="user@example.com",
            password_hash="hashed",
            nickname="홍길동",
        )
        assert user.uid == "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
        assert user.email == "user@example.com"
        assert user.password_hash == "hashed"
        assert user.nickname == "홍길동"

    def test_status_default_is_active(self):
        """status 미지정 시 ACTIVE가 기본값이다."""
        user = User(
            uid="usr_01",
            email="a@b.com",
            password_hash="h",
            nickname="유저",
        )
        assert user.status == UserStatus.ACTIVE

    def test_optional_fields_default_none(self):
        """profile_image_url, created_at, updated_at, last_login_at 기본값은 None이다."""
        user = User(
            uid="usr_01",
            email="a@b.com",
            password_hash="h",
            nickname="유저",
        )
        assert user.profile_image_url is None
        assert user.created_at is None
        assert user.updated_at is None
        assert user.last_login_at is None

    def test_optional_fields_can_be_set(self):
        """선택 필드를 지정할 수 있다."""
        now = datetime.now()
        user = User(
            uid="usr_01",
            email="a@b.com",
            password_hash="h",
            nickname="유저",
            status=UserStatus.SUSPENDED,
            profile_image_url="https://example.com/ava.png",
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )
        assert user.status == UserStatus.SUSPENDED
        assert user.profile_image_url == "https://example.com/ava.png"
        assert user.created_at is now
        assert user.updated_at is now
        assert user.last_login_at is now

    def test_is_dataclass(self):
        """User는 dataclass이다."""
        assert dataclasses.is_dataclass(User)
