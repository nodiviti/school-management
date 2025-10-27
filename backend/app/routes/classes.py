"""Class Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter

router = APIRouter(prefix="/classes")


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.HEADMASTER]))])
async def create_class(class_data: dict):
    """Create new class"""
    
    class_data['id'] = str(uuid.uuid4())
    class_data['created_at'] = datetime.now(timezone.utc).isoformat()
    class_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("classes", class_data)
    
    return class_data


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_classes(
    grade_level: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List all classes"""
    
    query = {}
    if grade_level:
        query["grade_level"] = grade_level
    if academic_year:
        query["academic_year"] = academic_year
    
    classes = await db_adapter.find_many("classes", query, limit=limit)
    
    return {
        "classes": classes,
        "total": len(classes),
        "skip": skip,
        "limit": limit
    }


@router.get("/{class_id}", dependencies=[Depends(get_current_user)])
async def get_class(class_id: str):
    """Get class by ID"""
    
    class_obj = await db_adapter.find_one("classes", {"id": class_id})
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    return class_obj