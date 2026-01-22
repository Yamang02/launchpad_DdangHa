"""
UserModel (SQLAlchemy ORM) 단위 테스트
spec: 001-signup-design — user/infrastructure/models.py UserModel
"""

from app.infrastructure.user.models import UserModel


class TestUserModel:
    """UserModel SQLAlchemy ORM"""

    def test_tablename_is_users(self):
        """__tablename__은 'users'이다."""
        assert UserModel.__tablename__ == "users"

    def test_has_uid_column(self):
        """uid 컬럼을 갖는다."""
        assert hasattr(UserModel, "uid")
        assert "uid" in UserModel.__table__.c

    def test_has_email_column(self):
        """email 컬럼을 갖는다."""
        assert hasattr(UserModel, "email")
        assert "email" in UserModel.__table__.c

    def test_has_password_hash_column(self):
        """password_hash 컬럼을 갖는다."""
        assert hasattr(UserModel, "password_hash")
        assert "password_hash" in UserModel.__table__.c

    def test_has_nickname_column(self):
        """nickname 컬럼을 갖는다."""
        assert hasattr(UserModel, "nickname")
        assert "nickname" in UserModel.__table__.c

    def test_has_status_column(self):
        """status 컬럼을 갖는다."""
        assert hasattr(UserModel, "status")
        assert "status" in UserModel.__table__.c

    def test_has_profile_image_url_column(self):
        """profile_image_url 컬럼을 갖는다 (nullable)."""
        assert hasattr(UserModel, "profile_image_url")
        assert "profile_image_url" in UserModel.__table__.c

    def test_has_created_at_updated_at_last_login_at(self):
        """created_at, updated_at, last_login_at 컬럼을 갖는다."""
        assert "created_at" in UserModel.__table__.c
        assert "updated_at" in UserModel.__table__.c
        assert "last_login_at" in UserModel.__table__.c

    def test_has_primary_key(self):
        """id 또는 uid 중 PK가 설정되어 있다 (마이그레이션 기준 id)."""
        pk = UserModel.__table__.primary_key
        assert pk is not None
        assert len(pk.columns) >= 1
