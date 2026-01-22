"""Auth 관련 DTO 정의"""

import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """회원가입 요청 DTO"""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    nickname: str = Field(min_length=2, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("비밀번호에 영문자가 포함되어야 합니다.")
        if not re.search(r"\d", v):
            raise ValueError("비밀번호에 숫자가 포함되어야 합니다.")
        return v


class SignupResponse(BaseModel):
    """회원가입 응답 DTO"""

    uid: str
    email: str
    nickname: str


class LoginRequest(BaseModel):
    """로그인 요청 DTO"""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """로그인 응답 DTO"""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # 초 단위 (예: 900 = 15분)
