"""User and Authentication Models"""
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserRole:
    """User role constants"""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    HEADMASTER = "headmaster"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    FINANCE = "finance"
    STAFF = "staff"
    LIBRARIAN = "librarian"


class UserModel(BaseModel):
    """User model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    password_hash: str
    role: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RefreshTokenModel(BaseModel):
    """Refresh token model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StudentModel(BaseModel):
    """Student model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Reference to UserModel
    student_number: str
    date_of_birth: datetime
    gender: str  # male, female, other
    address: str
    emergency_contact_name: str
    emergency_contact_phone: str
    blood_type: Optional[str] = None
    medical_notes: Optional[str] = None
    enrollment_date: datetime
    graduation_date: Optional[datetime] = None
    status: str = "active"  # active, inactive, graduated, expelled
    current_grade: Optional[str] = None
    current_class_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TeacherModel(BaseModel):
    """Teacher model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Reference to UserModel
    employee_number: str
    date_of_birth: datetime
    gender: str
    address: str
    phone: str
    qualification: str
    specialization: List[str] = []
    hire_date: datetime
    employment_type: str = "full_time"  # full_time, part_time, contract
    salary: Optional[float] = None
    status: str = "active"  # active, inactive, on_leave, retired
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ParentModel(BaseModel):
    """Parent/Guardian model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Reference to UserModel
    student_ids: List[str] = []  # References to StudentModel
    relationship: str  # father, mother, guardian
    occupation: Optional[str] = None
    phone: str
    address: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))