from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Language


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    preferred_language: Language = Language.de


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    preferred_language: Language


class UpdateLanguageRequest(BaseModel):
    preferred_language: Language
