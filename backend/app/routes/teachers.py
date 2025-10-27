"""Teacher Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter

router = APIRouter(prefix="/teachers")


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.HEADMASTER]))])
async def create_teacher(teacher_data: dict):
    """Create new teacher"""
    
    teacher_data['id'] = str(uuid.uuid4())
    teacher_data['created_at'] = datetime.now(timezone.utc).isoformat()
    teacher_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("teachers", teacher_data)
    
    return teacher_data


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_teachers(
    specialization: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List all teachers"""
    
    query = {}
    if status:
        query["status"] = status
    
    teachers = await db_adapter.find_many("teachers", query, limit=limit)
    
    return {
        "teachers": teachers,
        "total": len(teachers),
        "skip": skip,
        "limit": limit
    }


@router.get("/{teacher_id}", dependencies=[Depends(get_current_user)])
async def get_teacher(teacher_id: str):
    """Get teacher by ID"""
    
    teacher = await db_adapter.find_one("teachers", {"id": teacher_id})
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    return teacher


@router.patch("/{teacher_id}", dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.HEADMASTER]))])
async def update_teacher(teacher_id: str, update_data: dict):
    """Update teacher"""
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    success = await db_adapter.update_one("teachers", {"id": teacher_id}, update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    return {"message": "Teacher updated successfully"}