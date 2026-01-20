"""
API 공통 Response 스키마 테스트
spec: 000-foundation
"""
import pytest

from app.shared.schemas.response import ApiErrorResponse, ApiSuccessResponse


class TestApiSuccessResponse:
    """ApiSuccessResponse[data]"""

    def test_model_dump_has_success_true_and_data(self):
        """model_dump() → {"success": True, "data": ...}"""
        obj = ApiSuccessResponse(data={"uid": "usr_01ABC", "name": "테스트"})
        d = obj.model_dump()
        assert d["success"] is True
        assert d["data"] == {"uid": "usr_01ABC", "name": "테스트"}

    def test_model_dump_with_list_data(self):
        """data가 리스트여도 그대로 직렬화"""
        obj = ApiSuccessResponse(data=[1, 2, 3])
        d = obj.model_dump()
        assert d["success"] is True
        assert d["data"] == [1, 2, 3]


class TestApiErrorResponse:
    """ApiErrorResponse(error=ApiErrorBody)"""

    def test_model_dump_has_success_false_and_error(self):
        """model_dump() → {"success": False, "error": {code, message}}"""
        obj = ApiErrorResponse(
            error={"code": "VALIDATION_ERROR", "message": "입력값이 올바르지 않습니다."}
        )
        d = obj.model_dump()
        assert d["success"] is False
        assert d["error"]["code"] == "VALIDATION_ERROR"
        assert d["error"]["message"] == "입력값이 올바르지 않습니다."

    def test_model_dump_error_with_details(self):
        """error.details가 있으면 포함"""
        obj = ApiErrorResponse(
            error={
                "code": "VALIDATION_ERROR",
                "message": "오류",
                "details": [{"field": "email", "message": "형식 오류"}],
            }
        )
        d = obj.model_dump()
        assert d["error"]["details"] == [{"field": "email", "message": "형식 오류"}]
