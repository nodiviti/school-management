"""Academic Models"""
from datetime import datetime, timezone, time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class SubjectModel(BaseModel):
    """Subject/Course model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    description: Optional[str] = None
    credits: int = 1
    category: str  # core, elective, mandatory
    grade_level: str  # e.g., "10", "11", "12"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClassModel(BaseModel):
    """Class/Section model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "10-A", "Grade 10 Science"
    grade_level: str
    section: str
    academic_year: str  # e.g., "2024-2025"
    teacher_id: Optional[str] = None  # Class teacher/homeroom
    room_number: Optional[str] = None
    capacity: int = 40
    student_ids: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TimetableModel(BaseModel):
    """Class timetable/schedule model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    class_id: str
    subject_id: str
    teacher_id: str
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    room_number: Optional[str] = None
    academic_year: str
    semester: str  # 1, 2
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AttendanceModel(BaseModel):
    """Attendance record model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    class_id: str
    subject_id: Optional[str] = None
    date: datetime
    status: str  # present, absent, late, excused
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    qr_code_used: bool = False
    notes: Optional[str] = None
    marked_by: str  # teacher_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GradeModel(BaseModel):
    """Grade/Assessment model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    subject_id: str
    class_id: str
    assessment_type: str  # quiz, midterm, final, assignment, project
    assessment_name: str
    score: float
    max_score: float
    percentage: float
    grade_letter: Optional[str] = None  # A, B, C, D, F
    academic_year: str
    semester: str
    date: datetime
    teacher_id: str
    comments: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))