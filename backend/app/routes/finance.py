"""Finance Management Routes"""
from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_user, require_role
from app.models.user import UserRole
from app.database.base import db_adapter
from app.services.payment import get_payment_gateway

router = APIRouter(prefix="/finance")


@router.post("/invoices", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.FINANCE, UserRole.ADMIN]))])
async def create_invoice(invoice_data: dict):
    """Create invoice"""
    
    invoice_data['id'] = str(uuid.uuid4())
    invoice_data['invoice_number'] = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    invoice_data['created_at'] = datetime.now(timezone.utc).isoformat()
    invoice_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db_adapter.insert_one("invoices", invoice_data)
    
    return invoice_data


@router.get("/invoices", dependencies=[Depends(get_current_user)])
async def list_invoices(
    student_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List invoices"""
    
    query = {}
    if student_id:
        query["student_id"] = student_id
    if status:
        query["status"] = status
    
    invoices = await db_adapter.find_many("invoices", query, limit=limit)
    
    return {
        "invoices": invoices,
        "total": len(invoices),
        "skip": skip,
        "limit": limit
    }


@router.post("/payments", status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create payment transaction"""
    
    # Get invoice
    invoice = await db_adapter.find_one("invoices", {"id": payment_data['invoice_id']})
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Create payment via gateway
    try:
        gateway = get_payment_gateway()
        gateway_response = await gateway.create_payment(invoice)
        
        payment_data['id'] = str(uuid.uuid4())
        payment_data['payment_number'] = f"PAY-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        payment_data['gateway_transaction_id'] = gateway_response.get('transaction_id')
        payment_data['status'] = 'pending'
        payment_data['created_at'] = datetime.now(timezone.utc).isoformat()
        payment_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        await db_adapter.insert_one("payments", payment_data)
        
        return {
            "payment": payment_data,
            "payment_url": gateway_response.get('payment_url')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment creation failed: {str(e)}"
        )


@router.post("/webhooks/payment")
async def payment_webhook(request: Request):
    """Handle payment gateway webhooks"""
    
    payload = await request.json()
    signature = request.headers.get('X-Signature', '')
    
    try:
        gateway = get_payment_gateway()
        is_valid = await gateway.verify_webhook(payload, signature)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Update payment status
        # TODO: Implement payment status update logic
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )