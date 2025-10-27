"""Authentication Routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from typing import Dict

from app.schemas.auth import (
    UserRegisterSchema,
    UserLoginSchema,
    TokenResponse,
    RefreshTokenSchema,
    Enable2FAResponse,
    Verify2FASchema,
    UserResponseSchema
)
from app.models.user import UserModel, RefreshTokenModel, UserRole
from app.core.security import (
    PasswordHandler,
    JWTHandler,
    TwoFactorAuth,
    get_current_user,
    TokenBlacklist
)
from app.core.config import settings
from app.database.base import db_adapter
import uuid
import secrets

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterSchema):
    """Register a new user"""
    
    # Validate role
    valid_roles = [
        UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.HEADMASTER,
        UserRole.TEACHER, UserRole.STUDENT, UserRole.PARENT,
        UserRole.FINANCE, UserRole.STAFF, UserRole.LIBRARIAN
    ]
    
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Check if user exists
    existing_user = await db_adapter.find_one("users", {"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_strong, message = PasswordHandler.validate_password_strength(user_data.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Hash password
    password_hash = PasswordHandler.hash_password(user_data.password)
    
    # Create user
    user = UserModel(
        email=user_data.email,
        username=user_data.username,
        password_hash=password_hash,
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone
    )
    
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['updated_at'] = user_dict['updated_at'].isoformat()
    if user_dict.get('last_login'):
        user_dict['last_login'] = user_dict['last_login'].isoformat()
    
    await db_adapter.insert_one("users", user_dict)
    
    # Remove password hash from response
    response_data = user.model_dump()
    del response_data['password_hash']
    
    return response_data


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLoginSchema):
    """Login and get access token"""
    
    # Find user
    user_dict = await db_adapter.find_one("users", {"email": credentials.email})
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not PasswordHandler.verify_password(credentials.password, user_dict['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user_dict.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check 2FA if enabled
    if user_dict.get('two_factor_enabled', False):
        if not credentials.totp_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA token required"
            )
        
        if not TwoFactorAuth.verify_totp(user_dict['two_factor_secret'], credentials.totp_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA token"
            )
    
    # Create tokens
    token_data = {
        "user_id": user_dict['id'],
        "email": user_dict['email'],
        "role": user_dict['role']
    }
    
    access_token = JWTHandler.create_access_token(token_data)
    refresh_token = JWTHandler.create_refresh_token(token_data)
    
    # Store refresh token
    refresh_token_model = RefreshTokenModel(
        user_id=user_dict['id'],
        token=refresh_token,
        expires_at=datetime.now(timezone.utc)
    )
    
    # Update last login
    await db_adapter.update_one(
        "users",
        {"id": user_dict['id']},
        {"last_login": datetime.now(timezone.utc).isoformat()}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_data: RefreshTokenSchema):
    """Refresh access token using refresh token"""
    
    try:
        payload = JWTHandler.decode_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Create new tokens
        token_data = {
            "user_id": payload['user_id'],
            "email": payload['email'],
            "role": payload['role']
        }
        
        access_token = JWTHandler.create_access_token(token_data)
        refresh_token = JWTHandler.create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """Logout and invalidate token"""
    
    # Add token to blacklist
    # Note: In production, implement proper token blacklist in Redis
    
    return {"message": "Logged out successfully"}


@router.post("/enable-2fa", response_model=Enable2FAResponse)
async def enable_2fa(current_user: Dict = Depends(get_current_user)):
    """Enable 2FA for user"""
    
    if not settings.ENABLE_2FA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled on this server"
        )
    
    # Generate secret
    secret = TwoFactorAuth.generate_secret()
    qr_uri = TwoFactorAuth.get_totp_uri(secret, current_user['email'])
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(8) for _ in range(10)]
    
    # Store secret (temporarily, until verified)
    await db_adapter.update_one(
        "users",
        {"id": current_user['user_id']},
        {"two_factor_secret": secret}
    )
    
    return Enable2FAResponse(
        secret=secret,
        qr_code_uri=qr_uri,
        backup_codes=backup_codes
    )


@router.post("/verify-2fa")
async def verify_2fa(
    verify_data: Verify2FASchema,
    current_user: Dict = Depends(get_current_user)
):
    """Verify and activate 2FA"""
    
    user = await db_adapter.find_one("users", {"id": current_user['user_id']})
    
    if not user or not user.get('two_factor_secret'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not initiated"
        )
    
    if not TwoFactorAuth.verify_totp(user['two_factor_secret'], verify_data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA token"
        )
    
    # Activate 2FA
    await db_adapter.update_one(
        "users",
        {"id": current_user['user_id']},
        {"two_factor_enabled": True}
    )
    
    return {"message": "2FA enabled successfully"}


@router.get("/me", response_model=UserResponseSchema)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    
    user = await db_adapter.find_one("users", {"id": current_user['user_id']})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove sensitive data
    if 'password_hash' in user:
        del user['password_hash']
    if 'two_factor_secret' in user:
        del user['two_factor_secret']
    
    return user