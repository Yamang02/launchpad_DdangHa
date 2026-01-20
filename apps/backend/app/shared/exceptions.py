"""도메인 예외 정의"""


class DomainError(Exception):
    """도메인 로직 기본 예외"""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationError(DomainError):
    """입력값 검증 실패 예외"""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class DuplicateEmailError(DomainError):
    """이메일 중복 예외"""

    def __init__(self, email: str):
        super().__init__(f"이미 사용 중인 이메일입니다: {email}", "EMAIL_ALREADY_EXISTS")
        self.email = email
