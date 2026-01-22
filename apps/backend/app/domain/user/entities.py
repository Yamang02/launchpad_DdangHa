"""User 도메인 엔티티"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User:
    """User 도메인 엔티티 (Business ID 기준)"""

    uid: str
    email: str
    password_hash: str
    nickname: str
    status: UserStatus = UserStatus.ACTIVE
    profile_image_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None
