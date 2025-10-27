"""Authentication Schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegisterSchema(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    role: str
    phone: Optional[str] = None


class UserLoginSchema(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
    totp_token: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenSchema(BaseModel):
    """Refresh token schema"""
    refresh_token: str


class Enable2FAResponse(BaseModel):
    """2FA setup response"""
    secret: str
    qr_code_uri: str
    backup_codes: list[str]


class Verify2FASchema(BaseModel):
    """Verify 2FA schema"""
    token: str


class UserResponseSchema(BaseModel):
    """User response schema"""
    id: str
    email: str
    username: str
    role: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    last_login: Optional[datetime] = None
    created_at: datetime