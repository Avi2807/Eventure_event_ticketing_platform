from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, SeatingSection, Seat, Venue, User, Ticket

seating_bp = Blueprint('seating', __name__, url_prefix='/api/seating')

@seating_bp.route('/venues/<int:venue_id>/sections', methods=['POST'])
@jwt_required()
def create_section(venue_id):
    """Create a seating section (admin/organizer only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        data = request.get_json()
        
        required_fields = ['section_name', 'capacity', 'section_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        section = SeatingSection(
            venue_id=venue_id,
            section_name=data['section_name'],
            capacity=data['capacity'],
            section_type=data['section_type'],
            layout_config=data.get('layout_config')
        )
        
        db.session.add(section)
        db.session.commit()
        
        return jsonify({
            'message': 'Seating section created successfully',
            'section': section.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@seating_bp.route('/sections/<int:section_id>/seats', methods=['POST'])
@jwt_required()
def create_seats(section_id):
    """Create seats for a section (admin/organizer only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        section = SeatingSection.query.get(section_id)
        if not section:
            return jsonify({'error': 'Section not found'}), 404
        
        data = request.get_json()
        
        # Can create single seat or bulk seats
        if 'seats' in data:
            # Bulk creation
            seats_data = data['seats']
        elif 'row_number' in data and 'seat_number' in data:
            # Single seat
            seats_data = [data]
        else:
            return jsonify({'error': 'Invalid seat data'}), 400
        
        created_seats = []
        for seat_data in seats_data:
            seat = Seat(
                section_id=section_id,
                seat_number=seat_data['seat_number'],
                row_number=seat_data['row_number'],
                seat_type=seat_data.get('seat_type', 'regular')
            )
            db.session.add(seat)
            created_seats.append(seat)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(created_seats)} seat(s) created successfully',
            'seats': [seat.to_dict() for seat in created_seats]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@seating_bp.route('/venues/<int:venue_id>/chart', methods=['GET'])
def get_seating_chart(venue_id):
    """Get seating chart for a venue"""
    try:
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        sections = SeatingSection.query.filter_by(venue_id=venue_id).all()
        
        chart = {
            'venue_id': venue_id,
            'venue_name': venue.venue_name,
            'sections': []
        }
        
        for section in sections:
            seats = Seat.query.filter_by(section_id=section.section_id).all()
            
            # Get booked seats for active events
            booked_seat_ids = set()
            tickets = Ticket.query.join(Order).filter(
                Ticket.seat_id.in_([seat.seat_id for seat in seats]),
                Ticket.status == 'valid',
                Order.status == 'completed'
            ).all()
            booked_seat_ids = {ticket.seat_id for ticket in tickets}
            
            section_dict = section.to_dict()
            section_dict['seats'] = []
            
            for seat in seats:
                seat_dict = seat.to_dict()
                seat_dict['is_available'] = seat.seat_id not in booked_seat_ids
                section_dict['seats'].append(seat_dict)
            
            chart['sections'].append(section_dict)
        
        return jsonify(chart), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seating_bp.route('/events/<int:event_id>/available-seats', methods=['GET'])
def get_available_seats(event_id):
    """Get available seats for an event"""
    try:
        from models import Event
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        venue = event.venue
        sections = SeatingSection.query.filter_by(venue_id=venue.venue_id).all()
        
        # Get booked seats for this event
        booked_seat_ids = set()
        tickets = Ticket.query.join(Order).filter(
            Order.event_id == event_id,
            Ticket.seat_id.isnot(None),
            Ticket.status == 'valid',
            Order.status == 'completed'
        ).all()
        booked_seat_ids = {ticket.seat_id for ticket in tickets}
        
        available_seats = []
        for section in sections:
            seats = Seat.query.filter_by(section_id=section.section_id).all()
            for seat in seats:
                if seat.seat_id not in booked_seat_ids:
                    seat_dict = seat.to_dict()
                    seat_dict['section'] = section.to_dict()
                    available_seats.append(seat_dict)
        
        return jsonify({
            'event_id': event_id,
            'available_seats': available_seats,
            'total_available': len(available_seats)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

