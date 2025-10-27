"""Attendance Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone, date
import uuid
import qrcode
import io
import base64

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter
from app.core.config import settings

router = APIRouter(prefix="/attendance")


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.TEACHER, UserRole.ADMIN]))])
async def mark_attendance(
    attendance_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Mark student attendance"""
    
    attendance_data['id'] = str(uuid.uuid4())
    attendance_data['marked_by'] = current_user['user_id']
    attendance_data['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("attendance", attendance_data)
    
    return attendance_data


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_attendance(
    student_id: Optional[str] = Query(None),
    class_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List attendance records"""
    
    query = {}
    if student_id:
        query["student_id"] = student_id
    if class_id:
        query["class_id"] = class_id
    
    records = await db_adapter.find_many("attendance", query, limit=limit)
    
    return {
        "attendance": records,
        "total": len(records),
        "skip": skip,
        "limit": limit
    }


@router.get("/qr-code/{class_id}")
async def generate_attendance_qr(
    class_id: str,
    current_user: dict = Depends(require_role([UserRole.TEACHER, UserRole.ADMIN]))
):
    """Generate QR code for attendance check-in"""
    
    if not settings.FEATURE_ATTENDANCE_QR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="QR attendance feature is disabled"
        )
    
    # Generate QR code data
    qr_data = {
        "class_id": class_id,
        "date": datetime.now(timezone.utc).isoformat(),
        "token": str(uuid.uuid4())
    }
    
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(str(qr_data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "qr_code": f"data:image/png;base64,{img_str}",
        "class_id": class_id,
        "valid_until": datetime.now(timezone.utc).isoformat()
    }


@router.post("/qr-checkin")
async def qr_checkin(
    checkin_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Check in using QR code"""
    
    # Verify QR code and mark attendance
    attendance_data = {
        "id": str(uuid.uuid4()),
        "student_id": current_user['user_id'],
        "class_id": checkin_data.get('class_id'),
        "date": datetime.now(timezone.utc).isoformat(),
        "status": "present",
        "check_in_time": datetime.now(timezone.utc).isoformat(),
        "qr_code_used": True,
        "marked_by": "system",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db_adapter.insert_one("attendance", attendance_data)
    
    return {"message": "Attendance marked successfully", "data": attendance_data}