import uuid
from datetime import datetime
from models import db, Payment, Order, User
from flask import current_app

def generate_transaction_id():
    """Generate unique transaction ID"""
    return f"TXN_{uuid.uuid4().hex[:16].upper()}"

def process_payment(order_id, payment_method, amount, currency='USD'):
    """Process payment for an order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found", None
        
        # Enforce attendee-only purchase and wallet credits
        user = User.query.get(order.user_id)
        if not user:
            return False, "User not found", None
        if user.user_type != 'attendee':
            return False, "Only attendees can purchase tickets", None
        
        # Check credits
        user_credits = float(user.credits or 0.0)
        if user_credits < float(amount):
            return False, "Insufficient credits", None
        
        # Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # In a real application, integrate with payment gateway (Stripe, PayPal, etc.)
        # For now, simulate payment processing
        payment_gateway = current_app.config.get('PAYMENT_GATEWAY', 'stripe')
        
        # Simulate payment processing
        # In production, this would call the actual payment gateway API
        payment_status = 'completed'  # Simulated success
        
        # Create payment record
        payment = Payment(
            order_id=order_id,
            payment_method=payment_method,
            amount=amount,
            currency=currency,
            transaction_id=transaction_id,
            status=payment_status,
            payment_gateway=payment_gateway,
            processed_at=datetime.utcnow() if payment_status == 'completed' else None
        )
        
        db.session.add(payment)
        
        # Update order status
        if payment_status == 'completed':
            order.status = 'completed'
            # Deduct credits
            user.credits = user_credits - float(amount)
        
        db.session.commit()
        
        return True, "Payment processed successfully", payment
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Payment processing error: {str(e)}")
        return False, str(e), None

def process_refund(payment_id, amount, reason=None):
    """Process refund for a payment and refund credits to user account"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return False, "Payment not found", None
        
        if payment.status != 'completed':
            return False, "Payment not completed, cannot refund", None
        
        from models import Refund
        
        # Get the order and user to refund credits
        order = Order.query.get(payment.order_id)
        if not order:
            return False, "Order not found", None
        
        user = User.query.get(order.user_id)
        if not user:
            return False, "User not found", None
        
        # Create refund record
        refund = Refund(
            payment_id=payment_id,
            amount=amount,
            reason=reason,
            status='pending'
        )
        
        db.session.add(refund)
        
        # In production, call payment gateway refund API
        # For now, simulate refund processing
        refund.status = 'completed'
        refund.processed_at = datetime.utcnow()
        
        payment.status = 'refunded'
        
        # Refund credits to user account
        user_credits = float(user.credits or 0.0)
        refund_amount = float(amount)
        user.credits = user_credits + refund_amount
        
        # Update order status to refunded
        order.status = 'refunded'
        
        db.session.commit()
        
        return True, "Refund processed successfully", refund
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Refund processing error: {str(e)}")
        return False, str(e), None

