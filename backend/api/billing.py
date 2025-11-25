"""
API endpoints for payment and billing operations.
"""
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from services.payment_service import PaymentService
from utils.logging import logger

router = APIRouter(prefix="/api/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    """Request model for creating a checkout session."""
    email: EmailStr
    price_id: str
    success_url: str
    cancel_url: str
    metadata: Optional[Dict[str, str]] = None


class CheckoutResponse(BaseModel):
    """Response model for checkout session."""
    session_id: str
    url: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(request: CheckoutRequest):
    """
    Create a Stripe checkout session for subscription.
    
    Args:
        request: Checkout session parameters
        
    Returns:
        Checkout session details
    """
    try:
        result = await PaymentService.create_checkout_session(
            customer_email=request.email,
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata=request.metadata
        )
        return CheckoutResponse(**result)
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events.
    
    Args:
        request: Raw request object
        stripe_signature: Stripe signature header
        
    Returns:
        Success response
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    try:
        payload = await request.body()
        await PaymentService.handle_webhook(payload, stripe_signature)
        return {"status": "success"}
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/portal")
async def get_customer_portal(customer_id: str, return_url: str):
    """
    Get customer portal URL for managing subscriptions.
    
    Args:
        customer_id: Stripe customer ID
        return_url: URL to return to after portal session
        
    Returns:
        Portal URL
    """
    try:
        url = await PaymentService.get_customer_portal_url(customer_id, return_url)
        return {"url": url}
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portal session")
