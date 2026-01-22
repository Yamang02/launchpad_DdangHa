"""
JWT Handler 단위 테스트 (TDD - Phase 1)
spec: 002-login-design — JWT 토큰 생성/검증
"""

import os
import pytest
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

# 환경변수 설정 (테스트용)
os.environ["JWT_SECRET_KEY"] = "test-secret-key-minimum-32-bytes-long-for-testing"

from app.infrastructure.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_token_uid,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)


def test_create_access_token_returns_string():
    """create_access_token은 문자열 토큰을 반환한다."""
    data = {"sub": "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_includes_user_uid():
    """create_access_token은 사용자 UID를 포함한다."""
    user_uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
    token = create_access_token({"sub": user_uid})
    payload = verify_token(token)
    assert payload is not None
    assert payload.get("sub") == user_uid


def test_create_access_token_includes_expiration():
    """create_access_token은 만료 시간을 포함한다."""
    data = {"sub": "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"}
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload is not None
    assert "exp" in payload
    
    # 만료 시간이 약 15분 후인지 확인 (1분 오차 허용)
    exp_timestamp = payload["exp"]
    exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    expected_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    time_diff = abs((exp_time - expected_time).total_seconds())
    assert time_diff < 60  # 1분 이내


def test_create_access_token_includes_type():
    """create_access_token은 type이 'access'인지 확인한다."""
    data = {"sub": "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"}
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload is not None
    assert payload.get("type") == "access"


def test_create_refresh_token_returns_string():
    """create_refresh_token은 문자열 토큰을 반환한다."""
    uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
    token = create_refresh_token(uid)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_refresh_token_includes_user_uid():
    """create_refresh_token은 사용자 UID를 포함한다."""
    user_uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
    token = create_refresh_token(user_uid)
    payload = verify_token(token)
    assert payload is not None
    assert payload.get("uid") == user_uid


def test_create_refresh_token_includes_expiration():
    """create_refresh_token은 만료 시간을 포함한다."""
    uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
    token = create_refresh_token(uid)
    payload = verify_token(token)
    assert payload is not None
    assert "exp" in payload
    
    # 만료 시간이 약 7일 후인지 확인 (1시간 오차 허용)
    exp_timestamp = payload["exp"]
    exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    expected_time = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    time_diff = abs((exp_time - expected_time).total_seconds())
    assert time_diff < 3600  # 1시간 이내


def test_create_refresh_token_includes_type():
    """create_refresh_token은 type이 'refresh'인지 확인한다."""
    uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
    token = create_refresh_token(uid)
    payload = verify_token(token)
    assert payload is not None
    assert payload.get("type") == "refresh"


def test_verify_token_valid_returns_payload():
    """유효한 토큰을 검증하면 Payload를 반환한다."""
    data = {"sub": "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"}
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload is not None
    assert isinstance(payload, dict)
    assert payload.get("sub") == "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"


def test_verify_token_expired_returns_none():
    """만료된 토큰을 검증하면 None을 반환한다."""
    # 만료된 토큰 생성 (과거 시간으로 설정)
    import jwt
    secret_key = os.getenv("JWT_SECRET_KEY")
    expired_payload = {
        "sub": "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),  # 1분 전 만료
        "type": "access"
    }
    expired_token = jwt.encode(expired_payload, secret_key, algorithm="HS256")
    
    payload = verify_token(expired_token)
    assert payload is None


def test_verify_token_invalid_returns_none():
    """잘못된 토큰을 검증하면 None을 반환한다."""
    invalid_token = "invalid.token.string"
    payload = verify_token(invalid_token)
    assert payload is None


def test_verify_token_wrong_secret_returns_none():
    """잘못된 Secret Key로 서명된 토큰을 검증하면 None을 반환한다."""
    import jwt
    wrong_secret = "wrong-secret-key"
    payload_data = {
        "sub": "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "type": "access"
    }
    wrong_token = jwt.encode(payload_data, wrong_secret, algorithm="HS256")
    
    payload = verify_token(wrong_token)
    assert payload is None


def test_get_token_uid_from_access_token():
    """Access Token의 Payload에서 UID를 추출한다."""
    user_uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
    token = create_access_token({"sub": user_uid})
    payload = verify_token(token)
    assert payload is not None
    
    uid = get_token_uid(payload)
    assert uid == user_uid


def test_get_token_uid_from_refresh_token():
    """Refresh Token의 Payload에서 UID를 추출한다."""
    user_uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
    token = create_refresh_token(user_uid)
    payload = verify_token(token)
    assert payload is not None
    
    uid = get_token_uid(payload)
    assert uid == user_uid


def test_get_token_uid_returns_none_when_no_uid():
    """Payload에 uid가 없으면 None을 반환한다."""
    payload = {"some": "data", "exp": datetime.now(timezone.utc).timestamp()}
    uid = get_token_uid(payload)
    assert uid is None
