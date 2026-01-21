# tests.integration
"""
통합 테스트 전용 conftest.
테스트 DB 마이그레이션을 session 시작 시 1회 실행 (migrate_test_db 의존).
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def _ensure_migrate(migrate_test_db):
    """integration 폴더 테스트 수집 시 migrate_test_db를 사용해 스키마 적용."""
    yield
