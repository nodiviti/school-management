"""Academic Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time


class SubjectCreateSchema(BaseModel):
    """Subject creation schema"""
    code: str
    name: str
    description: Optional[str] = None
    credits: int = 1
    category: str
    grade_level: str


class ClassCreateSchema(BaseModel):
    """Class creation schema"""
    name: str
    grade_level: str
    section: str
    academic_year: str
    teacher_id: Optional[str] = None
    room_number: Optional[str] = None
    capacity: int = 40


class AttendanceCreateSchema(BaseModel):
    """Attendance creation schema"""
    student_id: str
    class_id: str
    subject_id: Optional[str] = None
    date: datetime
    status: str
    qr_code_used: bool = False
    notes: Optional[str] = None


class GradeCreateSchema(BaseModel):
    """Grade creation schema"""
    student_id: str
    subject_id: str
    class_id: str
    assessment_type: str
    assessment_name: str
    score: float
    max_score: float
    academic_year: str
    semester: str
    date: datetime
    comments: Optional[str] = None


class TimetableCreateSchema(BaseModel):
    """Timetable creation schema"""
    class_id: str
    subject_id: str
    teacher_id: str
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str
    end_time: str
    room_number: Optional[str] = None
    academic_year: str
    semester: str