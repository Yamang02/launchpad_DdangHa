"""API 공통 Response 스키마 (success/data, success/error)"""

from typing import Any, Literal

from pydantic import BaseModel


class ApiSuccessResponse(BaseModel):
    """성공 응답: { "success": true, "data": ... }"""

    success: Literal[True] = True
    data: Any


class ErrorDetail(BaseModel):
    """에러 상세 (필드별 검증 오류 등)"""

    field: str | None = None
    message: str


class ApiErrorBody(BaseModel):
    """에러 본문: code, message, details(선택)"""

    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ApiErrorResponse(BaseModel):
    """실패 응답: { "success": false, "error": { "code", "message", "details"? } }"""

    success: Literal[False] = False
    error: ApiErrorBody
