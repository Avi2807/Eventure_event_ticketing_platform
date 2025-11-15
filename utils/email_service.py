from flask import current_app
from flask_mail import Message, Mail
from datetime import datetime
from models import db, EmailNotification

mail = Mail()

def send_email(recipient, subject, body, html_body=None):
    """Send an email"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            html=html_body
        )
        mail.send(msg)
        return True, "Email sent successfully"
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False, str(e)

def create_email_notification(user_id, email_type, recipient_email, subject, order_id=None, event_id=None):
    """Create an email notification record"""
    notification = EmailNotification(
        user_id=user_id,
        order_id=order_id,
        event_id=event_id,
        email_type=email_type,
        recipient_email=recipient_email,
        subject=subject,
        status='pending'
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def send_order_confirmation(order_id):
    """Send order confirmation email"""
    from models import Order, User, Event, Ticket
    
    order = Order.query.get(order_id)
    if not order:
        return False, "Order not found"
    
    user = User.query.get(order.user_id)
    event = Event.query.get(order.event_id)
    tickets = Ticket.query.filter_by(order_id=order_id).all()
    
    subject = f"Order Confirmation - {order.order_number}"
    body = f"""
    Dear {user.first_name} {user.last_name},
    
    Thank you for your purchase!
    
    Order Number: {order.order_number}
    Event: {event.event_name}
    Date: {event.start_datetime.strftime('%Y-%m-%d %H:%M')}
    
    Tickets:
    """
    
    for ticket in tickets:
        body += f"\n- {ticket.attendee_name}: {ticket.ticket_number}\n"
    
    body += f"""
    Subtotal: ${order.subtotal}
    Discount: ${order.discount_amount}
    Tax: ${order.tax_amount}
    Total: ${order.total_amount}
    
    Your tickets have been sent to your email.
    
    Best regards,
    Event Management Team
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>Order Confirmation</h2>
        <p>Dear {user.first_name} {user.last_name},</p>
        <p>Thank you for your purchase!</p>
        <h3>Order Details</h3>
        <p><strong>Order Number:</strong> {order.order_number}</p>
        <p><strong>Event:</strong> {event.event_name}</p>
        <p><strong>Date:</strong> {event.start_datetime.strftime('%Y-%m-%d %H:%M')}</p>
        <h3>Tickets</h3>
        <ul>
    """
    
    for ticket in tickets:
        html_body += f"<li>{ticket.attendee_name}: {ticket.ticket_number}</li>"
    
    html_body += f"""
        </ul>
        <p><strong>Subtotal:</strong> ${order.subtotal}</p>
        <p><strong>Discount:</strong> ${order.discount_amount}</p>
        <p><strong>Tax:</strong> ${order.tax_amount}</p>
        <p><strong>Total:</strong> ${order.total_amount}</p>
        <p>Your tickets have been sent to your email.</p>
        <p>Best regards,<br>Event Management Team</p>
    </body>
    </html>
    """
    
    success, message = send_email(user.email, subject, body, html_body)
    
    # Update notification status
    notification = EmailNotification.query.filter_by(
        order_id=order_id,
        email_type='order_confirmation'
    ).first()
    
    if notification:
        notification.status = 'sent' if success else 'failed'
        notification.sent_at = datetime.utcnow() if success else None
        db.session.commit()
    
    return success, message

def send_ticket_issued(ticket_id):
    """Send ticket issued email with QR code"""
    from models import Ticket, Order, Event
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return False, "Ticket not found"
    
    order = Order.query.get(ticket.order_id)
    event = Event.query.get(order.event_id)
    
    subject = f"Your Ticket for {event.event_name}"
    body = f"""
    Dear {ticket.attendee_name},
    
    Your ticket has been issued!
    
    Ticket Number: {ticket.ticket_number}
    Event: {event.event_name}
    Date: {event.start_datetime.strftime('%Y-%m-%d %H:%M')}
    Venue: {event.venue.venue_name}
    
    Please present this ticket (QR code) at the event entrance.
    
    Best regards,
    Event Management Team
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>Your Ticket</h2>
        <p>Dear {ticket.attendee_name},</p>
        <p>Your ticket has been issued!</p>
        <h3>Ticket Details</h3>
        <p><strong>Ticket Number:</strong> {ticket.ticket_number}</p>
        <p><strong>Event:</strong> {event.event_name}</p>
        <p><strong>Date:</strong> {event.start_datetime.strftime('%Y-%m-%d %H:%M')}</p>
        <p><strong>Venue:</strong> {event.venue.venue_name}</p>
        <p>Please present this ticket (QR code) at the event entrance.</p>
        <p>Best regards,<br>Event Management Team</p>
    </body>
    </html>
    """
    
    success, message = send_email(ticket.attendee_email, subject, body, html_body)
    return success, message

def send_event_reminder(event_id, user_id):
    """Send event reminder email"""
    from models import Event, User
    
    event = Event.query.get(event_id)
    user = User.query.get(user_id)
    
    if not event or not user:
        return False, "Event or user not found"
    
    subject = f"Reminder: {event.event_name} is coming up!"
    body = f"""
    Dear {user.first_name} {user.last_name},
    
    This is a reminder that {event.event_name} is scheduled for:
    
    Date: {event.start_datetime.strftime('%Y-%m-%d %H:%M')}
    Venue: {event.venue.venue_name}
    Address: {event.venue.address}, {event.venue.city}
    
    We look forward to seeing you there!
    
    Best regards,
    Event Management Team
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>Event Reminder</h2>
        <p>Dear {user.first_name} {user.last_name},</p>
        <p>This is a reminder that <strong>{event.event_name}</strong> is scheduled for:</p>
        <p><strong>Date:</strong> {event.start_datetime.strftime('%Y-%m-%d %H:%M')}</p>
        <p><strong>Venue:</strong> {event.venue.venue_name}</p>
        <p><strong>Address:</strong> {event.venue.address}, {event.venue.city}</p>
        <p>We look forward to seeing you there!</p>
        <p>Best regards,<br>Event Management Team</p>
    </body>
    </html>
    """
    
    success, message = send_email(user.email, subject, body, html_body)
    return success, message

def send_refund_processed(refund_id):
    """Send refund processed email"""
    from models import Refund, Payment, Order, User
    
    refund = Refund.query.get(refund_id)
    if not refund:
        return False, "Refund not found"
    
    payment = Payment.query.get(refund.payment_id)
    order = Order.query.get(payment.order_id)
    user = User.query.get(order.user_id)
    
    subject = f"Refund Processed - Order {order.order_number}"
    body = f"""
    Dear {user.first_name} {user.last_name},
    
    Your refund has been processed.
    
    Refund Amount: ${refund.amount}
    Order Number: {order.order_number}
    Reason: {refund.reason or 'N/A'}
    
    The refund will be credited to your original payment method within 5-7 business days.
    
    Best regards,
    Event Management Team
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>Refund Processed</h2>
        <p>Dear {user.first_name} {user.last_name},</p>
        <p>Your refund has been processed.</p>
        <p><strong>Refund Amount:</strong> ${refund.amount}</p>
        <p><strong>Order Number:</strong> {order.order_number}</p>
        <p><strong>Reason:</strong> {refund.reason or 'N/A'}</p>
        <p>The refund will be credited to your original payment method within 5-7 business days.</p>
        <p>Best regards,<br>Event Management Team</p>
    </body>
    </html>
    """
    
    success, message = send_email(user.email, subject, body, html_body)
    return success, message

def send_event_cancelled(event_id):
    """Send event cancelled email to all ticket holders"""
    from models import Event, Order, User
    
    event = Event.query.get(event_id)
    if not event:
        return False, "Event not found"
    
    # Get all orders for this event
    orders = Order.query.filter_by(event_id=event_id, status='completed').all()
    
    for order in orders:
        user = User.query.get(order.user_id)
        subject = f"Event Cancelled: {event.event_name}"
        body = f"""
        Dear {user.first_name} {user.last_name},
        
        We regret to inform you that {event.event_name} has been cancelled.
        
        Your order (Order Number: {order.order_number}) will be automatically refunded.
        The refund will be processed within 5-7 business days.
        
        We apologize for any inconvenience.
        
        Best regards,
        Event Management Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Event Cancelled</h2>
            <p>Dear {user.first_name} {user.last_name},</p>
            <p>We regret to inform you that <strong>{event.event_name}</strong> has been cancelled.</p>
            <p>Your order (Order Number: {order.order_number}) will be automatically refunded.</p>
            <p>The refund will be processed within 5-7 business days.</p>
            <p>We apologize for any inconvenience.</p>
            <p>Best regards,<br>Event Management Team</p>
        </body>
        </html>
        """
        
        send_email(user.email, subject, body, html_body)
    
    return True, "Cancellation emails sent"

