"""User 인프라 저장소 (SQLAlchemy)"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.entities import User, UserStatus
from app.domain.user.repository import UserRepository
from app.infrastructure.user.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy AsyncSession 기반 UserRepository 구현"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: UserModel) -> User:
        """UserModel → User 도메인 엔티티"""
        return User(
            uid=orm.uid,
            email=orm.email,
            password_hash=orm.password_hash,
            nickname=orm.nickname,
            status=UserStatus(orm.status),
            profile_image_url=orm.profile_image_url,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            last_login_at=orm.last_login_at,
        )

    async def get_by_email(self, email: str) -> User | None:
        orm = (
            await self._session.execute(select(UserModel).where(UserModel.email == email))
        ).scalars().one_or_none()
        return self._to_entity(orm) if orm else None

    async def get_by_uid(self, uid: str) -> User | None:
        orm = (
            await self._session.execute(select(UserModel).where(UserModel.uid == uid))
        ).scalars().one_or_none()
        return self._to_entity(orm) if orm else None

    async def create(self, user: User) -> User:
        orm = UserModel(
            uid=user.uid,
            email=user.email,
            password_hash=user.password_hash,
            nickname=user.nickname,
            status=user.status.value,
            profile_image_url=user.profile_image_url,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_entity(orm)
