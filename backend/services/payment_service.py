"""
Payment service for handling Stripe subscriptions and billing.
"""
import stripe
from typing import Dict, Any, Optional
from utils.config import settings
from utils.logging import logger

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None


class PaymentService:
    """Service for managing Stripe payments and subscriptions."""
    
    @staticmethod
    async def create_checkout_session(
        customer_email: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for subscription.
        
        Args:
            customer_email: Customer's email address
            price_id: Stripe price ID for the subscription
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
            metadata: Optional metadata to attach to the session
            
        Returns:
            Dictionary containing session ID and URL
        """
        try:
            session = stripe.checkout.Session.create(
                customer_email=customer_email,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            
            logger.info(f"Created checkout session for {customer_email}")
            return {
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise
    
    @staticmethod
    async def handle_webhook(payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.
        
        Args:
            payload: Raw request body
            sig_header: Stripe signature header
            
        Returns:
            Event data
        """
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        if not webhook_secret:
            raise ValueError("Stripe webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            
            logger.info(f"Received Stripe webhook: {event['type']}")
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                await PaymentService._handle_successful_payment(session)
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                await PaymentService._handle_subscription_cancelled(subscription)
            
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise
    
    @staticmethod
    async def _handle_successful_payment(session: Dict[str, Any]):
        """Handle successful payment completion."""
        customer_email = session.get('customer_email')
        subscription_id = session.get('subscription')
        
        logger.info(f"Payment successful for {customer_email}, subscription: {subscription_id}")
        # TODO: Update user's subscription status in database
    
    @staticmethod
    async def _handle_subscription_cancelled(subscription: Dict[str, Any]):
        """Handle subscription cancellation."""
        subscription_id = subscription.get('id')
        customer_id = subscription.get('customer')
        
        logger.info(f"Subscription {subscription_id} cancelled for customer {customer_id}")
        # TODO: Update user's subscription status in database
    
    @staticmethod
    async def get_customer_portal_url(customer_id: str, return_url: str) -> str:
        """
        Create a customer portal session for managing subscriptions.
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session
            
        Returns:
            Portal session URL
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Error creating portal session: {e}")
            raise
