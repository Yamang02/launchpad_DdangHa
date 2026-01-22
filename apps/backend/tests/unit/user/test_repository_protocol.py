"""
UserRepository Protocol 단위 테스트
spec: 001-signup-design — UserRepository (get_by_email, get_by_uid, create)
"""
import pytest

from app.domain.user.entities import User
from app.domain.user.repository import UserRepository


class TestUserRepositoryProtocol:
    """UserRepository Protocol / ABC 계약"""

    def test_protocol_can_be_imported(self):
        """UserRepository를 import할 수 있다."""
        assert UserRepository is not None

    @pytest.mark.asyncio
    async def test_get_by_email_signature(self):
        """get_by_email(email: str) -> User | None 시그니처를 만족하는 구현이 가능하다."""
        # Protocol 계약 검증: get_by_email을 가진 구현체가 awaitable한 User | None 을 반환
        class FakeRepo(UserRepository):
            async def get_by_email(self, email: str) -> User | None:
                return None

            async def get_by_uid(self, uid: str) -> User | None:
                return None

            async def create(self, user: User) -> User:
                return user

        repo = FakeRepo()
        result = await repo.get_by_email("a@b.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_uid_signature(self):
        """get_by_uid(uid: str) -> User | None 시그니처를 만족하는 구현이 가능하다."""
        class FakeRepo(UserRepository):
            async def get_by_email(self, email: str) -> User | None:
                return None

            async def get_by_uid(self, uid: str) -> User | None:
                return None

            async def create(self, user: User) -> User:
                return user

        repo = FakeRepo()
        result = await repo.get_by_uid("usr_01ARZ3NDEKTSV4RRFFQ69G5FAV")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_signature(self, user: User):
        """create(user: User) -> User 시그니처를 만족하는 구현이 가능하다."""
        class FakeRepo(UserRepository):
            async def get_by_email(self, email: str) -> User | None:
                return None

            async def get_by_uid(self, uid: str) -> User | None:
                return None

            async def create(self, user: User) -> User:
                return user

        repo = FakeRepo()
        created = await repo.create(user)
        assert created.uid == user.uid
        assert created.email == user.email

    @pytest.mark.asyncio
    async def test_update_last_login_signature(self):
        """update_last_login(uid: str) -> None 시그니처를 만족하는 구현이 가능하다."""
        class FakeRepo(UserRepository):
            async def get_by_email(self, email: str) -> User | None:
                return None

            async def get_by_uid(self, uid: str) -> User | None:
                return None

            async def create(self, user: User) -> User:
                return user

            async def update_last_login(self, uid: str) -> None:
                pass

        repo = FakeRepo()
        await repo.update_last_login("usr_01ARZ3NDEKTSV4RRFFQ69G5FAV")
        # 시그니처 검증만 수행 (반환값이 None이므로 추가 검증 불필요)
