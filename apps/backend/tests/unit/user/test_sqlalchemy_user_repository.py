"""
SQLAlchemyUserRepository 단위 테스트
spec: 001-signup-design — user/infrastructure/repository.py
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.user.entities import User
from app.infrastructure.user.repository import SQLAlchemyUserRepository


def _make_mock_orm(*, uid: str, email: str, **kwargs) -> SimpleNamespace:
    """_to_entity가 기대하는 UserModel 형태의 mock 객체."""
    return SimpleNamespace(
        uid=uid,
        email=email,
        password_hash=kwargs.get("password_hash", "hashed"),
        nickname=kwargs.get("nickname", "닉네임"),
        status=kwargs.get("status", "active"),
        profile_image_url=kwargs.get("profile_image_url"),
        created_at=kwargs.get("created_at"),
        updated_at=kwargs.get("updated_at"),
        last_login_at=kwargs.get("last_login_at"),
    )


class TestSQLAlchemyUserRepository:
    """SQLAlchemyUserRepository"""

    def test_can_be_instantiated_with_session(self):
        """AsyncSession을 받아 인스턴스를 생성할 수 있다."""
        mock_session = MagicMock()
        repo = SQLAlchemyUserRepository(mock_session)
        assert repo is not None

    @pytest.mark.asyncio
    async def test_create_persists_user_and_returns_entity(self):
        """create(user)는 User를 저장하고 동일한 uid/email/nickname을 가진 User를 반환한다."""
        mock_session = MagicMock()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        repo = SQLAlchemyUserRepository(mock_session)
        user = User(
            uid="usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
            email="new@example.com",
            password_hash="hashed",
            nickname="신규유저",
        )

        created = await repo.create(user)

        assert created.uid == user.uid
        assert created.email == user.email
        assert created.nickname == user.nickname
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_email_returns_user_when_exists(self):
        """get_by_email(email)은 해당 이메일의 User가 있으면 반환한다."""
        mock_orm = _make_mock_orm(uid="usr_01ARZ3NDEKTSV4RRFFQ69G5FAV", email="exists@example.com")
        mock_result = MagicMock()
        mock_result.scalars.return_value.one_or_none.return_value = mock_orm
        mock_session = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        repo = SQLAlchemyUserRepository(mock_session)
        result = await repo.get_by_email("exists@example.com")
        assert isinstance(result, User) and result.email == "exists@example.com"
        mock_session.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_by_email_returns_none_when_not_exists(self):
        """get_by_email(email)은 해당 이메일이 없으면 None을 반환한다."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.one_or_none.return_value = None
        mock_session = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        repo = SQLAlchemyUserRepository(mock_session)
        result = await repo.get_by_email("missing@example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_uid_returns_user_when_exists(self):
        """get_by_uid(uid)는 해당 uid의 User가 있으면 반환한다."""
        uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
        mock_orm = _make_mock_orm(uid=uid, email="u@example.com")
        mock_result = MagicMock()
        mock_result.scalars.return_value.one_or_none.return_value = mock_orm
        mock_session = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        repo = SQLAlchemyUserRepository(mock_session)
        result = await repo.get_by_uid(uid)
        assert isinstance(result, User) and result.uid == uid
        mock_session.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_last_login(self):
        """update_last_login(uid)는 해당 uid의 사용자 last_login_at을 현재 시간(UTC)으로 업데이트한다."""
        uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        repo = SQLAlchemyUserRepository(mock_session)
        await repo.update_last_login(uid)

        # execute()가 호출되었는지 확인 (update 문 실행)
        mock_session.execute.assert_awaited_once()
        # commit()이 호출되었는지 확인
        mock_session.commit.assert_awaited_once()
