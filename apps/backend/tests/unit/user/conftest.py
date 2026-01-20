"""pytest fixtures for user 도메인 단위 테스트"""

import pytest

from app.user.domain.entities import User, UserStatus


@pytest.fixture
def user() -> User:
    """기본 User 도메인 엔티티 (uid: usr_ prefix + ULID 26자)."""
    return User(
        uid="usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
        email="user@example.com",
        password_hash="hashed",
        nickname="테스트유저",
        status=UserStatus.ACTIVE,
    )
