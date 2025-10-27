"""Facility and Resource Models"""
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


class DormitoryModel(BaseModel):
    """Dormitory/Hostel building model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    building_code: str
    address: Optional[str] = None
    gender: str  # male, female, mixed
    total_rooms: int
    total_capacity: int
    warden_id: Optional[str] = None  # staff user_id
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DormitoryRoomModel(BaseModel):
    """Dormitory room model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dormitory_id: str
    room_number: str
    floor: int
    capacity: int
    current_occupancy: int = 0
    room_type: str  # single, double, shared
    amenities: List[str] = []  # AC, WiFi, attached_bathroom
    monthly_fee: float
    is_available: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DormitoryAllocationModel(BaseModel):
    """Student dormitory allocation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    room_id: str
    dormitory_id: str
    bed_number: Optional[str] = None
    check_in_date: datetime
    check_out_date: Optional[datetime] = None
    academic_year: str
    status: str = "active"  # active, completed, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LibraryBookModel(BaseModel):
    """Library book model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    isbn: Optional[str] = None
    title: str
    author: str
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    category: str  # fiction, non-fiction, reference, textbook
    language: str = "English"
    total_copies: int = 1
    available_copies: int = 1
    shelf_location: Optional[str] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LibraryLoanModel(BaseModel):
    """Library book loan/borrow model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    book_id: str
    borrower_id: str  # student or teacher user_id
    borrower_type: str  # student, teacher, staff
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str = "borrowed"  # borrowed, returned, overdue, lost
    fine_amount: float = 0.0
    fine_paid: bool = False
    notes: Optional[str] = None
    issued_by: str  # librarian user_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))