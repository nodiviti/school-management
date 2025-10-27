"""Subject Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter

router = APIRouter(prefix="/subjects")


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.HEADMASTER]))])
async def create_subject(subject_data: dict):
    """Create new subject"""
    
    subject_data['id'] = str(uuid.uuid4())
    subject_data['created_at'] = datetime.now(timezone.utc).isoformat()
    subject_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("subjects", subject_data)
    
    return subject_data


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_subjects(
    grade_level: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List all subjects"""
    
    query = {}
    if grade_level:
        query["grade_level"] = grade_level
    if category:
        query["category"] = category
    
    subjects = await db_adapter.find_many("subjects", query, limit=limit)
    
    return {
        "subjects": subjects,
        "total": len(subjects),
        "skip": skip,
        "limit": limit
    }


@router.get("/{subject_id}", dependencies=[Depends(get_current_user)])
async def get_subject(subject_id: str):
    """Get subject by ID"""
    
    subject = await db_adapter.find_one("subjects", {"id": subject_id})
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    return subject