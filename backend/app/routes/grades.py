"""Grade Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter

router = APIRouter(prefix="/grades")


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.TEACHER, UserRole.ADMIN]))])
async def create_grade(
    grade_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create grade entry"""
    
    # Calculate percentage and letter grade
    percentage = (grade_data['score'] / grade_data['max_score']) * 100
    grade_data['percentage'] = round(percentage, 2)
    
    # Assign letter grade
    if percentage >= 90:
        grade_data['grade_letter'] = 'A'
    elif percentage >= 80:
        grade_data['grade_letter'] = 'B'
    elif percentage >= 70:
        grade_data['grade_letter'] = 'C'
    elif percentage >= 60:
        grade_data['grade_letter'] = 'D'
    else:
        grade_data['grade_letter'] = 'F'
    
    grade_data['id'] = str(uuid.uuid4())
    grade_data['teacher_id'] = current_user['user_id']
    grade_data['created_at'] = datetime.now(timezone.utc).isoformat()
    grade_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("grades", grade_data)
    
    return grade_data


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_grades(
    student_id: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    class_id: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List grades"""
    
    query = {}
    if student_id:
        query["student_id"] = student_id
    if subject_id:
        query["subject_id"] = subject_id
    if class_id:
        query["class_id"] = class_id
    if academic_year:
        query["academic_year"] = academic_year
    
    grades = await db_adapter.find_many("grades", query, limit=limit)
    
    return {
        "grades": grades,
        "total": len(grades),
        "skip": skip,
        "limit": limit
    }


@router.get("/transcript/{student_id}")
async def get_transcript(
    student_id: str,
    academic_year: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get student transcript"""
    
    query = {"student_id": student_id}
    if academic_year:
        query["academic_year"] = academic_year
    
    grades = await db_adapter.find_many("grades", query, limit=1000)
    
    # Calculate GPA and aggregate by subject
    subjects = {}
    for grade in grades:
        subject_id = grade['subject_id']
        if subject_id not in subjects:
            subjects[subject_id] = []
        subjects[subject_id].append(grade)
    
    transcript = {
        "student_id": student_id,
        "academic_year": academic_year,
        "subjects": subjects,
        "total_grades": len(grades)
    }
    
    return transcript