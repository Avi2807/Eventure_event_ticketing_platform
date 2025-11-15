from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Venue, User, VenueBooking
from datetime import datetime

venues_bp = Blueprint('venues', __name__, url_prefix='/api/venues')

@venues_bp.route('', methods=['GET'])
def get_venues():
    """Get all venues with optional filters"""
    try:
        city = request.args.get('city')
        country = request.args.get('country')
        min_capacity = request.args.get('min_capacity', type=int)
        
        query = Venue.query
        
        if city:
            query = query.filter(Venue.city.ilike(f'%{city}%'))
        if country:
            query = query.filter(Venue.country.ilike(f'%{country}%'))
        if min_capacity:
            query = query.filter(Venue.capacity >= min_capacity)
        
        venues = query.all()
        
        return jsonify([venue.to_dict() for venue in venues]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@venues_bp.route('/<int:venue_id>', methods=['GET'])
def get_venue(venue_id):
    """Get venue by ID"""
    try:
        venue = Venue.query.get(venue_id)
        
        if not venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        venue_dict = venue.to_dict()
        venue_dict['seating_sections'] = [section.to_dict() for section in venue.seating_sections]
        
        return jsonify(venue_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@venues_bp.route('', methods=['POST'])
@jwt_required()
def create_venue():
    """Create a new venue (admin/organizer only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        required_fields = ['venue_name', 'address', 'city', 'country', 'capacity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        venue = Venue(
            venue_name=data['venue_name'],
            address=data['address'],
            city=data['city'],
            state=data.get('state'),
            country=data['country'],
            postal_code=data.get('postal_code'),
            capacity=data['capacity'],
            description=data.get('description'),
            amenities=data.get('amenities')
        )
        
        db.session.add(venue)
        db.session.commit()
        
        return jsonify({
            'message': 'Venue created successfully',
            'venue': venue.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@venues_bp.route('/<int:venue_id>/bookings', methods=['POST'])
@jwt_required()
def create_venue_booking(venue_id):
    """Create a venue booking"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        data = request.get_json()
        
        required_fields = ['booking_start', 'booking_end', 'booking_cost']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        booking_start = datetime.fromisoformat(data['booking_start'].replace('Z', '+00:00'))
        booking_end = datetime.fromisoformat(data['booking_end'].replace('Z', '+00:00'))
        
        # Check for overlapping bookings
        overlapping = VenueBooking.query.filter(
            VenueBooking.venue_id == venue_id,
            VenueBooking.status == 'confirmed',
            VenueBooking.booking_start < booking_end,
            VenueBooking.booking_end > booking_start
        ).first()
        
        if overlapping:
            return jsonify({'error': 'Venue is already booked for this time period'}), 400
        
        booking = VenueBooking(
            venue_id=venue_id,
            event_id=data.get('event_id'),
            booking_start=booking_start,
            booking_end=booking_end,
            booking_cost=data['booking_cost'],
            status='pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Venue booking created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@venues_bp.route('/<int:venue_id>/bookings', methods=['GET'])
def get_venue_bookings(venue_id):
    """Get bookings for a venue"""
    try:
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        bookings = VenueBooking.query.filter_by(venue_id=venue_id).all()
        
        return jsonify([booking.to_dict() for booking in bookings]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

