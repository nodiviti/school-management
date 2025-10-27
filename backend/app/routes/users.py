"""User Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter

router = APIRouter(prefix="/users")


@router.get("/", dependencies=[Depends(require_role([UserRole.SUPERADMIN, UserRole.ADMIN]))])
async def list_users(
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List all users with filters"""
    
    query = {}
    if role:
        query["role"] = role
    if is_active is not None:
        query["is_active"] = is_active
    
    users = await db_adapter.find_many("users", query, limit=limit)
    
    # Remove sensitive data
    for user in users:
        if 'password_hash' in user:
            del user['password_hash']
        if 'two_factor_secret' in user:
            del user['two_factor_secret']
    
    return {
        "users": users,
        "total": len(users),
        "skip": skip,
        "limit": limit
    }


@router.get("/{user_id}", dependencies=[Depends(get_current_user)])
async def get_user(user_id: str):
    """Get user by ID"""
    
    user = await db_adapter.find_one("users", {"id": user_id})
    
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


@router.patch("/{user_id}", dependencies=[Depends(require_role([UserRole.SUPERADMIN, UserRole.ADMIN]))])
async def update_user(user_id: str, update_data: dict):
    """Update user"""
    
    # Remove fields that shouldn't be updated directly
    protected_fields = ['id', 'password_hash', 'created_at']
    for field in protected_fields:
        update_data.pop(field, None)
    
    success = await db_adapter.update_one("users", {"id": user_id}, update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User updated successfully"}


@router.delete("/{user_id}", dependencies=[Depends(require_role([UserRole.SUPERADMIN]))])
async def delete_user(user_id: str):
    """Delete user (superadmin only)"""
    
    success = await db_adapter.delete_one("users", {"id": user_id})
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}