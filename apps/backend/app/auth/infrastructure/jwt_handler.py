"""JWT 토큰 생성 및 검증 유틸리티"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: Dict[str, str]) -> str:
    """Access Token 생성

    Args:
        data: 토큰에 포함할 데이터 (최소한 "sub": user_uid 포함)

    Returns:
        JWT Access Token 문자열
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(uid: str) -> str:
    """Refresh Token 생성

    Args:
        uid: 사용자 Business ID (예: "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV")

    Returns:
        JWT Refresh Token 문자열
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"uid": uid, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """토큰 검증 및 디코딩

    Args:
        token: JWT 토큰 문자열

    Returns:
        검증 성공 시 Payload 딕셔너리, 실패 시 None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_uid(payload: Dict[str, Any]) -> Optional[str]:
    """Payload에서 사용자 UID 추출

    Args:
        payload: JWT Payload 딕셔너리

    Returns:
        사용자 UID 또는 None
    """
    return payload.get("sub") or payload.get("uid")
