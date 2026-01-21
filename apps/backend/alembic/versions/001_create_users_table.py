"""001_create_users_table

Revision ID: 001
Revises:
Create Date: 2025-01-19

"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uid", sa.String(30), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("nickname", sa.String(50), nullable=False),
        sa.Column("profile_image_url", sa.String(500), nullable=True),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uid"),
        sa.UniqueConstraint("email"),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'suspended')",
            name="chk_status",
        ),
    )

    op.create_index("idx_users_uid", "users", ["uid"])
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_status", "users", ["status"])
    op.create_index("idx_users_created_at", "users", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_users_created_at", table_name="users")
    op.drop_index("idx_users_status", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_index("idx_users_uid", table_name="users")
    op.drop_table("users")
