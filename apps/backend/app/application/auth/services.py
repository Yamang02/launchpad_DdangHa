"""Auth 애플리케이션 서비스"""

from app.application.auth.dtos import SignupRequest, SignupResponse
from app.shared.exceptions import DuplicateEmailError
from app.shared.security import hash_password
from app.shared.uid import generate_user_uid
from app.domain.user.entities import User, UserStatus
from app.domain.user.repository import UserRepository


class AuthService:
    """인증 관련 비즈니스 로직"""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def signup(self, request: SignupRequest) -> SignupResponse:
        """회원가입 처리

        Args:
            request: 회원가입 요청 데이터

        Returns:
            생성된 사용자 정보

        Raises:
            DuplicateEmailError: 이메일이 이미 존재하는 경우
        """
        existing_user = await self._user_repository.get_by_email(request.email)
        if existing_user:
            raise DuplicateEmailError(request.email)

        user = User(
            uid=generate_user_uid(),
            email=request.email,
            password_hash=hash_password(request.password),
            nickname=request.nickname,
            status=UserStatus.ACTIVE,
        )

        created_user = await self._user_repository.create(user)

        return SignupResponse(
            uid=created_user.uid,
            email=created_user.email,
            nickname=created_user.nickname,
        )
