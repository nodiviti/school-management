"""Dormitory Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter

router = APIRouter(prefix="/dormitory")


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.HEADMASTER]))])
async def create_dormitory(dormitory_data: dict):
    """Create dormitory"""
    
    dormitory_data['id'] = str(uuid.uuid4())
    dormitory_data['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("dormitories", dormitory_data)
    
    return dormitory_data


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_dormitories(
    gender: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List dormitories"""
    
    query = {}
    if gender:
        query["gender"] = gender
    
    dormitories = await db_adapter.find_many("dormitories", query, limit=limit)
    
    return {
        "dormitories": dormitories,
        "total": len(dormitories),
        "skip": skip,
        "limit": limit
    }


@router.post("/rooms", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))])
async def create_room(room_data: dict):
    """Create dormitory room"""
    
    room_data['id'] = str(uuid.uuid4())
    room_data['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("dormitory_rooms", room_data)
    
    return room_data


@router.post("/allocations", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))])
async def allocate_room(allocation_data: dict):
    """Allocate student to room"""
    
    # Check room availability
    room = await db_adapter.find_one("dormitory_rooms", {"id": allocation_data['room_id']})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    if room['current_occupancy'] >= room['capacity']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is full"
        )
    
    allocation_data['id'] = str(uuid.uuid4())
    allocation_data['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("dormitory_allocations", allocation_data)
    
    # Update room occupancy
    await db_adapter.update_one(
        "dormitory_rooms",
        {"id": allocation_data['room_id']},
        {"current_occupancy": room['current_occupancy'] + 1}
    )
    
    return allocation_data