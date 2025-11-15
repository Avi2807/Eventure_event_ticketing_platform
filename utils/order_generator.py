import uuid
from datetime import datetime
from models import db, Order, Ticket, TicketType, PromotionalCode, EventAnalytics
from utils.qr_generator import generate_qr_code  # kept import style if needed elsewhere (not used now)
from utils.payment_processor import process_payment
from utils.email_service import send_order_confirmation, send_ticket_issued, create_email_notification
from flask import current_app

def generate_order_number():
    """Generate unique order number"""
    return f"ORD_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"

def generate_ticket_number():
    """Generate unique ticket number"""
    return f"TKT_{uuid.uuid4().hex[:16].upper()}"

def calculate_order_totals(ticket_items, promo_code=None, tax_rate=0.10):
    """Calculate order totals"""
    subtotal = 0.0
    
    for item in ticket_items:
        ticket_type = TicketType.query.get(item['ticket_type_id'])
        if not ticket_type:
            continue
        quantity = item.get('quantity', 1)
        subtotal += float(ticket_type.price) * quantity
    
    # Apply promotional code
    discount_amount = 0.0
    promo_id = None
    
    if promo_code:
        promo = PromotionalCode.query.filter_by(code=promo_code).first()
        if promo:
            is_valid, message = promo.is_valid()
            if is_valid:
                discount_amount = promo.calculate_discount(subtotal)
                promo_id = promo.promo_id
    
    # Calculate tax
    tax_amount = (subtotal - discount_amount) * tax_rate
    
    # Calculate total
    total_amount = subtotal - discount_amount + tax_amount
    
    return {
        'subtotal': round(subtotal, 2),
        'discount_amount': round(discount_amount, 2),
        'tax_amount': round(tax_amount, 2),
        'total_amount': round(total_amount, 2),
        'promo_id': promo_id
    }

def create_order(user_id, event_id, ticket_items, promo_code=None, payment_method='credit_card'):
    """Create order and tickets"""
    try:
        # Coerce event_id to int
        try:
            event_id = int(event_id)
        except Exception:
            return False, "Invalid event id", None
        # Validate ticket availability
        for item in ticket_items:
            tt_id = int(item['ticket_type_id'])
            ticket_type = TicketType.query.get(tt_id)
            if not ticket_type:
                return False, f"Ticket type {tt_id} not found", None
            
            quantity = item.get('quantity', 1)
            if ticket_type.quantity_available < quantity:
                return False, f"Insufficient tickets available for {ticket_type.type_name}", None
            
            if int(ticket_type.event_id) != int(event_id):
                return False, "Ticket type does not belong to this event", None
        
        # Calculate totals
        totals = calculate_order_totals(ticket_items, promo_code, current_app.config.get('TAX_RATE', 0.10))
        
        # Create order
        order = Order(
            user_id=user_id,
            event_id=event_id,
            promo_id=totals['promo_id'],
            order_number=generate_order_number(),
            subtotal=totals['subtotal'],
            discount_amount=totals['discount_amount'],
            tax_amount=totals['tax_amount'],
            total_amount=totals['total_amount'],
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order_id
        
        # Create tickets
        tickets = []
        for item in ticket_items:
            ticket_type = TicketType.query.get(item['ticket_type_id'])
            quantity = item.get('quantity', 1)
            attendee_info = item.get('attendees', [])
            
            for i in range(quantity):
                attendee = attendee_info[i] if i < len(attendee_info) else attendee_info[0] if attendee_info else {}
                
                ticket_number = generate_ticket_number()
                ticket = Ticket(
                    order_id=order.order_id,
                    ticket_type_id=ticket_type.ticket_type_id,
                    seat_id=item.get('seat_id'),
                    ticket_number=ticket_number,
                    attendee_name=attendee.get('name', ''),
                    attendee_email=attendee.get('email', ''),
                    price_paid=float(ticket_type.price),
                    status='valid'
                )
                
                db.session.add(ticket)
                tickets.append(ticket)
                
                # Update ticket type availability (simulating trigger)
                ticket_type.quantity_available -= 1
        
        # Update promotional code usage (simulating trigger)
        if totals['promo_id']:
            promo = PromotionalCode.query.get(totals['promo_id'])
            if promo:
                promo.usage_count += 1
        
        db.session.commit()
        
        # Process payment
        success, message, payment = process_payment(
            order.order_id,
            payment_method,
            totals['total_amount']
        )
        
        if not success:
            # Rollback order if payment fails
            db.session.rollback()
            return False, f"Payment failed: {message}", None
        
        # Update event analytics on successful purchase
        try:
            analytics = EventAnalytics.query.filter_by(event_id=event_id).first()
            if not analytics:
                analytics = EventAnalytics(
                    event_id=event_id,
                    total_tickets_sold=0,
                    total_revenue=0.00,
                    total_attendees=0,
                    tickets_by_type={},
                    revenue_by_type={}
                )
                db.session.add(analytics)
                db.session.flush()
            if analytics:
                # Aggregate counts by ticket type for this order
                tickets_by_type_delta = {}
                revenue_by_type_delta = {}
                for item in ticket_items:
                    tt = TicketType.query.get(int(item['ticket_type_id']))
                    if not tt:
                        continue
                    qty = int(item.get('quantity', 1))
                    tickets_by_type_delta[tt.type_name] = tickets_by_type_delta.get(tt.type_name, 0) + qty
                    revenue_by_type_delta[tt.type_name] = revenue_by_type_delta.get(tt.type_name, 0.0) + float(tt.price) * qty
                
                # Update totals
                analytics.total_tickets_sold = int(analytics.total_tickets_sold or 0) + sum(tickets_by_type_delta.values())
                analytics.total_revenue = float(analytics.total_revenue or 0.0) + float(totals['total_amount'])
                analytics.total_attendees = int(analytics.total_attendees or 0) + sum(tickets_by_type_delta.values())
                
                # Update JSON breakdowns
                current_tickets_by_type = analytics.tickets_by_type or {}
                current_revenue_by_type = analytics.revenue_by_type or {}
                for k, v in tickets_by_type_delta.items():
                    current_tickets_by_type[k] = int(current_tickets_by_type.get(k, 0)) + v
                for k, v in revenue_by_type_delta.items():
                    current_revenue_by_type[k] = float(current_revenue_by_type.get(k, 0.0)) + float(v)
                analytics.tickets_by_type = current_tickets_by_type
                analytics.revenue_by_type = current_revenue_by_type
                
                db.session.commit()
        except Exception as e:
            current_app.logger.warning(f"Analytics update failed: {str(e)}")
        
        # Create email notification
        from models import User
        user = User.query.get(user_id)
        create_email_notification(
            user_id=user_id,
            email_type='order_confirmation',
            recipient_email=user.email,
            subject=f"Order Confirmation - {order.order_number}",
            order_id=order.order_id,
            event_id=event_id
        )
        
        # Send emails
        send_order_confirmation(order.order_id)
        for ticket in tickets:
            send_ticket_issued(ticket.ticket_id)
        
        return True, "Order created successfully", order
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Order creation error: {str(e)}")
        return False, str(e), None

