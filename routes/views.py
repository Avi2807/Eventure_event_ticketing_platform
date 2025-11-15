from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from functools import wraps
import requests

views_bp = Blueprint('views', __name__)

def get_current_user():
    """Get current user from JWT token in request"""
    try:
        # Try to verify JWT from Authorization header
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            try:
                user_id_int = int(user_id)
            except Exception:
                user_id_int = None
            from models import User
            user = User.query.get(user_id_int) if user_id_int is not None else None
            return user.to_dict() if user else None
    except Exception:
        # If JWT verification fails, return None (frontend will handle auth)
        pass
    return None

@views_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html', current_user=get_current_user())

@views_bp.route('/login')
def login():
    """Login page"""
    # Don't check server-side auth - let frontend handle it
    # If user has token in localStorage, frontend will redirect
    return render_template('login.html', current_user=None)

@views_bp.route('/register')
def register():
    """Register page"""
    if get_current_user():
        return redirect(url_for('views.dashboard'))
    return render_template('register.html', current_user=None)

@views_bp.route('/dashboard')
def dashboard():
    """Dashboard page - redirects to appropriate dashboard based on user type"""
    # Don't redirect - let frontend JavaScript handle authentication
    # The dashboard template will check localStorage for token
    user = get_current_user()  # Optional - will be None if no token in headers
    return render_template('dashboard.html', current_user=user)

@views_bp.route('/dashboard/attendee')
def dashboard_attendee():
    """Attendee dashboard page"""
    user = get_current_user()  # Optional
    return render_template('dashboard_attendee.html', current_user=user)

@views_bp.route('/dashboard/organizer')
def dashboard_organizer():
    """Organizer dashboard page"""
    user = get_current_user()  # Optional
    return render_template('dashboard_organizer.html', current_user=user)

@views_bp.route('/events')
def events_list():
    """Events listing page"""
    return render_template('events.html', current_user=get_current_user())

@views_bp.route('/events/<int:event_id>')
def event_detail_page(event_id):
    """Event detail page"""
    return render_template('event_detail.html', current_user=get_current_user())

@views_bp.route('/events/create')
def create_event():
    """Create event page"""
    # Don't check server-side auth - let frontend JavaScript handle authentication
    # The template will check localStorage for token and redirect if needed
    user = get_current_user()  # Optional - will be None if no token in headers
    return render_template('create_event.html', current_user=user)

@views_bp.route('/orders/<int:order_id>')
def order_detail_page(order_id):
    """Order detail page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('views.login'))
    return render_template('order_detail.html', current_user=user)

@views_bp.route('/profile')
def profile():
    """User profile page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('views.login'))
    return render_template('profile.html', current_user=user)

@views_bp.route('/logout')
def logout():
    """Logout - clears session and redirects"""
    session.clear()
    # Frontend JavaScript will handle clearing localStorage
    return redirect(url_for('views.index'))

