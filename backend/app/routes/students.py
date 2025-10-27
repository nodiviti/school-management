"""Student Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.models.user import StudentModel
from app.database.base import db_adapter

router = APIRouter(prefix="/students")


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.HEADMASTER]))])
async def create_student(student_data: dict):
    """Create new student"""
    
    # Verify user exists
    user = await db_adapter.find_one("users", {"id": student_data.get('user_id')})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if student already exists for this user
    existing = await db_adapter.find_one("students", {"user_id": student_data.get('user_id')})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile already exists for this user"
        )
    
    student_data['id'] = str(uuid.uuid4())
    student_data['created_at'] = datetime.now(timezone.utc).isoformat()
    student_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("students", student_data)
    
    return student_data


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_students(
    grade: Optional[str] = Query(None),
    class_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List all students with filters"""
    
    query = {}
    if grade:
        query["current_grade"] = grade
    if class_id:
        query["current_class_id"] = class_id
    if status:
        query["status"] = status
    
    students = await db_adapter.find_many("students", query, limit=limit)
    
    return {
        "students": students,
        "total": len(students),
        "skip": skip,
        "limit": limit
    }


@router.get("/{student_id}", dependencies=[Depends(get_current_user)])
async def get_student(student_id: str):
    """Get student by ID"""
    
    student = await db_adapter.find_one("students", {"id": student_id})
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return student


@router.patch("/{student_id}", dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.HEADMASTER, UserRole.TEACHER]))])
async def update_student(student_id: str, update_data: dict):
    """Update student"""
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    success = await db_adapter.update_one("students", {"id": student_id}, update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return {"message": "Student updated successfully"}


@router.delete("/{student_id}", dependencies=[Depends(require_role([UserRole.SUPERADMIN, UserRole.ADMIN]))])
async def delete_student(student_id: str):
    """Delete student"""
    
    success = await db_adapter.delete_one("students", {"id": student_id})
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return {"message": "Student deleted successfully"}