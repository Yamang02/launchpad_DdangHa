"""User 도메인 저장소 인터페이스"""

from typing import Protocol

from app.domain.user.entities import User


class UserRepository(Protocol):
    """User 저장소 Protocol (get_by_email, get_by_uid, create)"""

    async def get_by_email(self, email: str) -> User | None:
        ...

    async def get_by_uid(self, uid: str) -> User | None:
        ...

    async def create(self, user: User) -> User:
        ...
