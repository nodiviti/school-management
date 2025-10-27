"""Finance and Payment Models"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class FeeTypeModel(BaseModel):
    """Fee type configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # tuition, library, exam, transport, dormitory
    description: Optional[str] = None
    amount: float
    currency: str = "IDR"
    frequency: str  # one_time, monthly, quarterly, semester, annual
    is_mandatory: bool = True
    grade_levels: List[str] = []  # applicable grades
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvoiceModel(BaseModel):
    """Invoice model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    student_id: str
    academic_year: str
    semester: Optional[str] = None
    items: List[Dict[str, Any]] = []  # [{fee_type_id, amount, description}]
    subtotal: float
    discount: float = 0.0
    tax: float = 0.0
    total_amount: float
    currency: str = "IDR"
    due_date: datetime
    status: str = "pending"  # pending, paid, overdue, cancelled
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaymentModel(BaseModel):
    """Payment transaction model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payment_number: str
    invoice_id: str
    student_id: str
    amount: float
    currency: str = "IDR"
    payment_method: str  # cash, bank_transfer, credit_card, e_wallet
    payment_gateway: Optional[str] = None  # midtrans, xendit, stripe
    gateway_transaction_id: Optional[str] = None
    status: str = "pending"  # pending, completed, failed, refunded
    paid_at: Optional[datetime] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    processed_by: Optional[str] = None  # user_id of finance staff
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExpenseModel(BaseModel):
    """Expense/Expenditure model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    expense_number: str
    category: str  # salary, utilities, supplies, maintenance, other
    description: str
    amount: float
    currency: str = "IDR"
    date: datetime
    payment_method: str
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    approved_by: Optional[str] = None  # user_id
    status: str = "pending"  # pending, approved, paid, rejected
    created_by: str  # user_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))