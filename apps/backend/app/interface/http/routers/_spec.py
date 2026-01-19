"""
API 표준 응답 형식 검증용 스펙 라우터
GET /_spec/ok, /_spec/error — 000-foundation
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.shared.schemas.response import ApiErrorBody, ApiErrorResponse, ApiSuccessResponse

router = APIRouter(prefix="/_spec", tags=["_spec"])


@router.get("/ok")
async def spec_ok():
    """200, success=True, data 존재"""
    body = ApiSuccessResponse(data={"ok": True}).model_dump()
    return JSONResponse(content=body, status_code=200)


@router.get("/error")
async def spec_error():
    """400, success=False, error.code, error.message"""
    body = ApiErrorResponse(
        error=ApiErrorBody(code="SPEC_ERROR", message="spec error endpoint")
    ).model_dump()
    return JSONResponse(content=body, status_code=400)
