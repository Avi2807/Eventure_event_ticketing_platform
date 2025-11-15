from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    user_type = db.Column(db.Enum('organizer', 'attendee', 'admin'), nullable=False, default='attendee', index=True)
    credits = db.Column(db.Numeric(10, 2), nullable=False, default=500.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organized_events = db.relationship('Event', backref='organizer', lazy=True, foreign_keys='Event.organizer_id')
    orders = db.relationship('Order', backref='user', lazy=True)
    email_notifications = db.relationship('EmailNotification', backref='user', lazy=True)
    check_ins_performed = db.relationship('CheckIn', backref='checked_in_by_user', lazy=True, foreign_keys='CheckIn.checked_in_by')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'date_of_birth': str(self.date_of_birth) if self.date_of_birth else None,
            'user_type': self.user_type,
            'credits': float(self.credits) if self.credits is not None else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Venue(db.Model):
    """Venue model"""
    __tablename__ = 'venues'
    
    venue_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    venue_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    capacity = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text)
    amenities = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='venue', lazy=True)
    seating_sections = db.relationship('SeatingSection', backref='venue', lazy=True, cascade='all, delete-orphan')
    venue_bookings = db.relationship('VenueBooking', backref='venue', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'venue_id': self.venue_id,
            'venue_name': self.venue_name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'capacity': self.capacity,
            'description': self.description,
            'amenities': self.amenities,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Event(db.Model):
    """Event model"""
    __tablename__ = 'events'
    
    event_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    organizer_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False, index=True)
    venue_id = db.Column(db.BigInteger, db.ForeignKey('venues.venue_id', ondelete='RESTRICT'), nullable=False, index=True)
    event_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)
    start_datetime = db.Column(db.DateTime, nullable=False, index=True)
    end_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('draft', 'published', 'cancelled', 'completed'), nullable=False, default='draft', index=True)
    banner_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket_types = db.relationship('TicketType', backref='event', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='event', lazy=True)
    promotional_codes = db.relationship('PromotionalCode', backref='event', lazy=True, cascade='all, delete-orphan')
    check_ins = db.relationship('CheckIn', backref='event', lazy=True)
    email_notifications = db.relationship('EmailNotification', backref='event', lazy=True)
    event_analytics = db.relationship('EventAnalytics', backref='event', lazy=True, uselist=False, cascade='all, delete-orphan')
    venue_bookings = db.relationship('VenueBooking', backref='event', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'organizer_id': self.organizer_id,
            'venue_id': self.venue_id,
            'event_name': self.event_name,
            'description': self.description,
            'category': self.category,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'status': self.status,
            'banner_image': self.banner_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SeatingSection(db.Model):
    """Seating Section model"""
    __tablename__ = 'seating_sections'
    
    section_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    venue_id = db.Column(db.BigInteger, db.ForeignKey('venues.venue_id', ondelete='CASCADE'), nullable=False, index=True)
    section_name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    section_type = db.Column(db.Enum('seated', 'standing', 'vip'), nullable=False, default='seated')
    layout_config = db.Column(db.JSON)
    
    # Relationships
    seats = db.relationship('Seat', backref='section', lazy=True, cascade='all, delete-orphan')
    ticket_types = db.relationship('TicketType', backref='section', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('venue_id', 'section_name', name='unique_venue_section'),)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'section_id': self.section_id,
            'venue_id': self.venue_id,
            'section_name': self.section_name,
            'capacity': self.capacity,
            'section_type': self.section_type,
            'layout_config': self.layout_config
        }

class Seat(db.Model):
    """Seat model"""
    __tablename__ = 'seats'
    
    seat_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('seating_sections.section_id', ondelete='CASCADE'), nullable=False, index=True)
    seat_number = db.Column(db.String(20), nullable=False)
    row_number = db.Column(db.String(10), nullable=False)
    seat_type = db.Column(db.Enum('regular', 'accessible', 'premium'), nullable=False, default='regular')
    
    # Relationships
    tickets = db.relationship('Ticket', backref='seat', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('section_id', 'row_number', 'seat_number', name='unique_section_seat'),)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'seat_id': self.seat_id,
            'section_id': self.section_id,
            'seat_number': self.seat_number,
            'row_number': self.row_number,
            'seat_type': self.seat_type
        }

class TicketType(db.Model):
    """Ticket Type model"""
    __tablename__ = 'ticket_types'
    
    ticket_type_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.event_id', ondelete='CASCADE'), nullable=False, index=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('seating_sections.section_id', ondelete='SET NULL'), nullable=True, index=True)
    type_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_total = db.Column(db.Integer, nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False)
    sale_start = db.Column(db.DateTime, nullable=False, index=True)
    sale_end = db.Column(db.DateTime, nullable=False, index=True)
    min_purchase = db.Column(db.Integer, default=1)
    max_purchase = db.Column(db.Integer, default=10)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='ticket_type', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'ticket_type_id': self.ticket_type_id,
            'event_id': self.event_id,
            'section_id': self.section_id,
            'type_name': self.type_name,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'quantity_total': self.quantity_total,
            'quantity_available': self.quantity_available,
            'sale_start': self.sale_start.isoformat() if self.sale_start else None,
            'sale_end': self.sale_end.isoformat() if self.sale_end else None,
            'min_purchase': self.min_purchase,
            'max_purchase': self.max_purchase
        }

class PromotionalCode(db.Model):
    """Promotional Code model"""
    __tablename__ = 'promotional_codes'
    
    promo_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.event_id', ondelete='CASCADE'), nullable=True, index=True)
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    discount_type = db.Column(db.Enum('percentage', 'fixed_amount'), nullable=False)
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    usage_limit = db.Column(db.Integer)
    usage_count = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime, nullable=False, index=True)
    valid_until = db.Column(db.DateTime, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='promo_code', lazy=True)
    
    def is_valid(self):
        """Check if promotional code is valid"""
        now = datetime.utcnow()
        if not self.is_active:
            return False, "Promotional code is not active"
        if now < self.valid_from:
            return False, "Promotional code is not yet valid"
        if now > self.valid_until:
            return False, "Promotional code has expired"
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, "Promotional code usage limit reached"
        return True, "Valid"
    
    def calculate_discount(self, amount):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            return float(amount * self.discount_value / 100)
        else:
            return float(min(self.discount_value, amount))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'promo_id': self.promo_id,
            'event_id': self.event_id,
            'code': self.code,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else None,
            'usage_limit': self.usage_limit,
            'usage_count': self.usage_count,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Order(db.Model):
    """Order model"""
    __tablename__ = 'orders'
    
    order_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False, index=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.event_id', ondelete='RESTRICT'), nullable=False, index=True)
    promo_id = db.Column(db.BigInteger, db.ForeignKey('promotional_codes.promo_id', ondelete='SET NULL'), nullable=True)
    order_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded'), nullable=False, default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='order', lazy=True)
    payments = db.relationship('Payment', backref='order', lazy=True)
    email_notifications = db.relationship('EmailNotification', backref='order', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'event_id': self.event_id,
            'promo_id': self.promo_id,
            'order_number': self.order_number,
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'discount_amount': float(self.discount_amount) if self.discount_amount else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Ticket(db.Model):
    """Ticket model"""
    __tablename__ = 'tickets'
    
    ticket_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders.order_id', ondelete='RESTRICT'), nullable=False, index=True)
    ticket_type_id = db.Column(db.BigInteger, db.ForeignKey('ticket_types.ticket_type_id', ondelete='RESTRICT'), nullable=False, index=True)
    seat_id = db.Column(db.BigInteger, db.ForeignKey('seats.seat_id', ondelete='SET NULL'), nullable=True, index=True)
    ticket_number = db.Column(db.String(100), nullable=False, unique=True, index=True)
    attendee_name = db.Column(db.String(200), nullable=False)
    attendee_email = db.Column(db.String(255), nullable=False, index=True)
    price_paid = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('valid', 'used', 'cancelled', 'refunded'), nullable=False, default='valid', index=True)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    check_ins = db.relationship('CheckIn', backref='ticket', lazy=True, uselist=False)
    refunds = db.relationship('Refund', backref='ticket', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'ticket_id': self.ticket_id,
            'order_id': self.order_id,
            'ticket_type_id': self.ticket_type_id,
            'seat_id': self.seat_id,
            'ticket_number': self.ticket_number,
            'attendee_name': self.attendee_name,
            'attendee_email': self.attendee_email,
            'price_paid': float(self.price_paid) if self.price_paid else None,
            'status': self.status,
            'checked_in_at': self.checked_in_at.isoformat() if self.checked_in_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Payment(db.Model):
    """Payment model"""
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders.order_id', ondelete='RESTRICT'), nullable=False, index=True)
    payment_method = db.Column(db.Enum('credit_card', 'debit_card', 'paypal', 'bank_transfer'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    transaction_id = db.Column(db.String(255), nullable=False, unique=True, index=True)
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded'), nullable=False, default='pending', index=True)
    payment_gateway = db.Column(db.String(50), nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    refunds = db.relationship('Refund', backref='payment', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'payment_id': self.payment_id,
            'order_id': self.order_id,
            'payment_method': self.payment_method,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'payment_gateway': self.payment_gateway,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Refund(db.Model):
    """Refund model"""
    __tablename__ = 'refunds'
    
    refund_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    payment_id = db.Column(db.BigInteger, db.ForeignKey('payments.payment_id', ondelete='RESTRICT'), nullable=False, index=True)
    ticket_id = db.Column(db.BigInteger, db.ForeignKey('tickets.ticket_id', ondelete='SET NULL'), nullable=True, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'completed', 'failed'), nullable=False, default='pending', index=True)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'refund_id': self.refund_id,
            'payment_id': self.payment_id,
            'ticket_id': self.ticket_id,
            'amount': float(self.amount) if self.amount else None,
            'reason': self.reason,
            'status': self.status,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CheckIn(db.Model):
    """Check-in model"""
    __tablename__ = 'check_ins'
    
    check_in_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.BigInteger, db.ForeignKey('tickets.ticket_id', ondelete='RESTRICT'), nullable=False, index=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.event_id', ondelete='RESTRICT'), nullable=False, index=True)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    check_in_method = db.Column(db.Enum('qr_scan', 'manual', 'mobile_app'), nullable=False)
    checked_in_by = db.Column(db.BigInteger, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    location = db.Column(db.String(100))
    
    __table_args__ = (db.UniqueConstraint('ticket_id', name='unique_ticket_checkin'),)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'check_in_id': self.check_in_id,
            'ticket_id': self.ticket_id,
            'event_id': self.event_id,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_in_method': self.check_in_method,
            'checked_in_by': self.checked_in_by,
            'location': self.location
        }

class EmailNotification(db.Model):
    """Email Notification model"""
    __tablename__ = 'email_notifications'
    
    notification_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False, index=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders.order_id', ondelete='SET NULL'), nullable=True, index=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.event_id', ondelete='SET NULL'), nullable=True, index=True)
    email_type = db.Column(db.Enum('order_confirmation', 'ticket_issued', 'event_reminder', 'refund_processed', 'event_cancelled'), nullable=False)
    recipient_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('pending', 'sent', 'failed', 'bounced'), nullable=False, default='pending', index=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'event_id': self.event_id,
            'email_type': self.email_type,
            'recipient_email': self.recipient_email,
            'subject': self.subject,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EventAnalytics(db.Model):
    """Event Analytics model"""
    __tablename__ = 'event_analytics'
    
    analytics_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.event_id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    total_tickets_sold = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Numeric(12, 2), default=0.00)
    total_attendees = db.Column(db.Integer, default=0)
    tickets_by_type = db.Column(db.JSON)
    revenue_by_type = db.Column(db.JSON)
    promo_codes_used = db.Column(db.JSON)
    attendance_rate = db.Column(db.Numeric(5, 2), default=0.00)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'analytics_id': self.analytics_id,
            'event_id': self.event_id,
            'total_tickets_sold': self.total_tickets_sold,
            'total_revenue': float(self.total_revenue) if self.total_revenue else None,
            'total_attendees': self.total_attendees,
            'tickets_by_type': self.tickets_by_type,
            'revenue_by_type': self.revenue_by_type,
            'promo_codes_used': self.promo_codes_used,
            'attendance_rate': float(self.attendance_rate) if self.attendance_rate else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class VenueBooking(db.Model):
    """Venue Booking model"""
    __tablename__ = 'venue_bookings'
    
    booking_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    venue_id = db.Column(db.BigInteger, db.ForeignKey('venues.venue_id', ondelete='RESTRICT'), nullable=False, index=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.event_id', ondelete='SET NULL'), nullable=True, index=True)
    booking_start = db.Column(db.DateTime, nullable=False, index=True)
    booking_end = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled'), nullable=False, default='pending', index=True)
    booking_cost = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'booking_id': self.booking_id,
            'venue_id': self.venue_id,
            'event_id': self.event_id,
            'booking_start': self.booking_start.isoformat() if self.booking_start else None,
            'booking_end': self.booking_end.isoformat() if self.booking_end else None,
            'status': self.status,
            'booking_cost': float(self.booking_cost) if self.booking_cost else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

