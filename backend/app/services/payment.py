"""Payment Gateway Integration Service"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import hmac
import hashlib
import base64
import json
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class PaymentGateway(ABC):
    """Abstract payment gateway interface"""
    
    @abstractmethod
    async def create_payment(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment transaction"""
        pass
    
    @abstractmethod
    async def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check payment status"""
        pass
    
    @abstractmethod
    async def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify webhook signature"""
        pass


class MidtransGateway(PaymentGateway):
    """Midtrans payment gateway"""
    
    def __init__(self):
        self.server_key = settings.MIDTRANS_SERVER_KEY
        self.is_production = settings.MIDTRANS_IS_PRODUCTION
        self.base_url = (
            "https://app.midtrans.com" if self.is_production 
            else "https://app.sandbox.midtrans.com"
        )
        self.api_url = (
            "https://api.midtrans.com" if self.is_production 
            else "https://api.sandbox.midtrans.com"
        )
    
    async def create_payment(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Midtrans payment"""
        try:
            payload = {
                "transaction_details": {
                    "order_id": invoice_data["invoice_number"],
                    "gross_amount": int(invoice_data["total_amount"])
                },
                "customer_details": invoice_data.get("customer_details", {}),
                "item_details": invoice_data.get("items", [])
            }
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Basic {self._get_auth_string()}"
            }
            
            response = requests.post(
                f"{self.api_url}/v2/charge",
                json=payload,
                headers=headers
            )
            
            return response.json()
        except Exception as e:
            logger.error(f"Midtrans payment creation failed: {e}")
            return {"error": str(e)}
    
    async def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check Midtrans payment status"""
        try:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Basic {self._get_auth_string()}"
            }
            
            response = requests.get(
                f"{self.api_url}/v2/{transaction_id}/status",
                headers=headers
            )
            
            return response.json()
        except Exception as e:
            logger.error(f"Midtrans status check failed: {e}")
            return {"error": str(e)}
    
    async def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify Midtrans webhook signature"""
        order_id = payload.get("order_id")
        status_code = payload.get("status_code")
        gross_amount = payload.get("gross_amount")
        
        signature_key = f"{order_id}{status_code}{gross_amount}{self.server_key}"
        calculated_signature = hashlib.sha512(signature_key.encode()).hexdigest()
        
        return calculated_signature == signature
    
    def _get_auth_string(self) -> str:
        """Get base64 encoded auth string"""
        auth = f"{self.server_key}:"
        return base64.b64encode(auth.encode()).decode()


class XenditGateway(PaymentGateway):
    """Xendit payment gateway"""
    
    def __init__(self):
        self.secret_key = settings.XENDIT_SECRET_KEY
        self.base_url = "https://api.xendit.co"
    
    async def create_payment(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Xendit invoice"""
        try:
            payload = {
                "external_id": invoice_data["invoice_number"],
                "amount": invoice_data["total_amount"],
                "description": invoice_data.get("description", "School Payment"),
                "currency": invoice_data.get("currency", "IDR")
            }
            
            headers = {
                "Authorization": f"Basic {self._get_auth_string()}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/v2/invoices",
                json=payload,
                headers=headers
            )
            
            return response.json()
        except Exception as e:
            logger.error(f"Xendit payment creation failed: {e}")
            return {"error": str(e)}
    
    async def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check Xendit payment status"""
        try:
            headers = {
                "Authorization": f"Basic {self._get_auth_string()}"
            }
            
            response = requests.get(
                f"{self.base_url}/v2/invoices/{transaction_id}",
                headers=headers
            )
            
            return response.json()
        except Exception as e:
            logger.error(f"Xendit status check failed: {e}")
            return {"error": str(e)}
    
    async def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify Xendit webhook signature"""
        webhook_token = settings.XENDIT_WEBHOOK_TOKEN
        calculated_signature = hmac.new(
            webhook_token.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        return calculated_signature == signature
    
    def _get_auth_string(self) -> str:
        """Get base64 encoded auth string"""
        return base64.b64encode(f"{self.secret_key}:".encode()).decode()


class StripeGateway(PaymentGateway):
    """Stripe payment gateway (placeholder)"""
    
    async def create_payment(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Stripe payment intent"""
        # TODO: Implement Stripe integration
        return {"message": "Stripe integration pending"}
    
    async def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check Stripe payment status"""
        return {"message": "Stripe integration pending"}
    
    async def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify Stripe webhook"""
        return True


class BayarindGateway(PaymentGateway):
    """Bayarind payment gateway (placeholder)"""
    
    async def create_payment(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Bayarind payment"""
        # TODO: Implement Bayarind integration
        return {"message": "Bayarind integration pending"}
    
    async def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check Bayarind payment status"""
        return {"message": "Bayarind integration pending"}
    
    async def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify Bayarind webhook"""
        return True


def get_payment_gateway() -> PaymentGateway:
    """Factory function to get configured payment gateway"""
    gateway_map = {
        "midtrans": MidtransGateway,
        "xendit": XenditGateway,
        "stripe": StripeGateway,
        "bayarind": BayarindGateway
    }
    
    gateway_class = gateway_map.get(settings.PAYMENT_GATEWAY)
    if not gateway_class:
        raise ValueError(f"Unsupported payment gateway: {settings.PAYMENT_GATEWAY}")
    
    return gateway_class()