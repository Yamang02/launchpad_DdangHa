"""Auth HTTP 라우터"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.dtos import SignupRequest, SignupResponse
from app.auth.application.services import AuthService
from app.shared.database import get_db
from app.shared.exceptions import DuplicateEmailError, ValidationError
from app.shared.schemas.response import ApiErrorBody, ApiErrorResponse, ErrorDetail
from app.user.infrastructure.repository import SQLAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    """AuthService 의존성: DB 세션 → UserRepository → AuthService"""
    return AuthService(SQLAlchemyUserRepository(session))


@router.post(
    "/signup",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="이메일과 비밀번호로 새 계정을 생성합니다.",
)
async def signup(
    request: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """회원가입 엔드포인트"""
    try:
        response = await auth_service.signup(request)
        return {"success": True, "data": response.model_dump()}
    except DuplicateEmailError as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ApiErrorResponse(
                error=ApiErrorBody(
                    code=e.code,
                    message="이미 사용 중인 이메일입니다.",
                )
            ).model_dump(),
        )
    except ValidationError as e:
        details = (
            [ErrorDetail(field=e.field, message=e.message)]
            if e.field
            else None
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ApiErrorResponse(
                error=ApiErrorBody(
                    code=e.code,
                    message=e.message,
                    details=details,
                )
            ).model_dump(),
        )
