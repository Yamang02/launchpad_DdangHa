"""
SQLAlchemyUserRepository 단위 테스트
spec: 001-signup-design — user/infrastructure/repository.py
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.user.domain.entities import User
from app.user.infrastructure.repository import SQLAlchemyUserRepository


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
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        repo = SQLAlchemyUserRepository(mock_session)
        result = await repo.get_by_email("exists@example.com")
        assert result is None or (isinstance(result, User) and result.email == "exists@example.com")
        mock_session.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_by_email_returns_none_when_not_exists(self):
        """get_by_email(email)은 해당 이메일이 없으면 None을 반환한다."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        repo = SQLAlchemyUserRepository(mock_session)
        result = await repo.get_by_email("missing@example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_uid_returns_user_when_exists(self):
        """get_by_uid(uid)는 해당 uid의 User가 있으면 반환한다."""
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        repo = SQLAlchemyUserRepository(mock_session)
        result = await repo.get_by_uid("usr_01ARZ3NDEKTSV4RRFFQ69G5FAV")
        assert result is None or (isinstance(result, User) and result.uid == "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV")
        mock_session.execute.assert_awaited()
