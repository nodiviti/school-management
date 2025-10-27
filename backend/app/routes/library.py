"""Library Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter

router = APIRouter(prefix="/library")


@router.post("/books", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.LIBRARIAN, UserRole.ADMIN]))])
async def add_book(book_data: dict):
    """Add book to library"""
    
    book_data['id'] = str(uuid.uuid4())
    book_data['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("library_books", book_data)
    
    return book_data


@router.get("/books", dependencies=[Depends(get_current_user)])
async def list_books(
    category: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    isbn: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List library books"""
    
    query = {}
    if category:
        query["category"] = category
    if author:
        query["author"] = author
    if isbn:
        query["isbn"] = isbn
    
    books = await db_adapter.find_many("library_books", query, limit=limit)
    
    return {
        "books": books,
        "total": len(books),
        "skip": skip,
        "limit": limit
    }


@router.post("/loans", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.LIBRARIAN]))])
async def borrow_book(
    loan_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Borrow a book"""
    
    # Check book availability
    book = await db_adapter.find_one("library_books", {"id": loan_data['book_id']})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book['available_copies'] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book not available"
        )
    
    loan_data['id'] = str(uuid.uuid4())
    loan_data['issued_by'] = current_user['user_id']
    loan_data['loan_date'] = datetime.now(timezone.utc).isoformat()
    loan_data['due_date'] = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
    loan_data['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("library_loans", loan_data)
    
    # Update book availability
    await db_adapter.update_one(
        "library_books",
        {"id": loan_data['book_id']},
        {"available_copies": book['available_copies'] - 1}
    )
    
    return loan_data


@router.patch("/loans/{loan_id}/return", dependencies=[Depends(require_role([UserRole.LIBRARIAN]))])
async def return_book(loan_id: str):
    """Return a borrowed book"""
    
    loan = await db_adapter.find_one("library_loans", {"id": loan_id})
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Update loan
    return_date = datetime.now(timezone.utc).isoformat()
    await db_adapter.update_one(
        "library_loans",
        {"id": loan_id},
        {
            "return_date": return_date,
            "status": "returned"
        }
    )
    
    # Update book availability
    book = await db_adapter.find_one("library_books", {"id": loan['book_id']})
    await db_adapter.update_one(
        "library_books",
        {"id": loan['book_id']},
        {"available_copies": book['available_copies'] + 1}
    )
    
    return {"message": "Book returned successfully", "return_date": return_date}