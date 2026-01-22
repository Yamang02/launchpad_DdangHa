"""User 도메인 저장소 인터페이스"""

from typing import Protocol

from app.domain.user.entities import User


class UserRepository(Protocol):
    """User 저장소 Protocol (get_by_email, get_by_uid, create, update_last_login)"""

    async def get_by_email(self, email: str) -> User | None:
        ...

    async def get_by_uid(self, uid: str) -> User | None:
        ...

    async def create(self, user: User) -> User:
        ...

    async def update_last_login(self, uid: str) -> None:
        """마지막 로그인 시간 업데이트

        Args:
            uid: 사용자 Business ID
        """
        ...
