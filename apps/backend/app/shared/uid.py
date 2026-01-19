"""ULID 기반 Business ID 생성 유틸리티"""

from ulid import ULID


def generate_uid(prefix: str) -> str:
    """prefix가 붙은 ULID 생성

    Args:
        prefix: 도메인 식별 접두사 (예: "usr_", "rtk_")

    Returns:
        "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV" 형태의 문자열
    """
    return f"{prefix}{ULID()}"


def generate_user_uid() -> str:
    """User 도메인용 UID 생성"""
    return generate_uid("usr_")
