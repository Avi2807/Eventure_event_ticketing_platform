from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CheckIn, Ticket, User, Event
from datetime import datetime

checkins_bp = Blueprint('checkins', __name__, url_prefix='/api/check-ins')

@checkins_bp.route('', methods=['POST'])
@jwt_required()
def create_check_in():
    """Create a check-in record"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Only staff/admin can perform check-ins
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        required_fields = ['ticket_id', 'event_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        ticket = Ticket.query.get(data['ticket_id'])
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        event = Event.query.get(data['event_id'])
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check if ticket belongs to this event
        if ticket.order.event_id != event.event_id:
            return jsonify({'error': 'Ticket does not belong to this event'}), 400
        
        # Check if ticket is already checked in
        if ticket.status == 'used':
            return jsonify({'error': 'Ticket already checked in'}), 400
        
        # Check if check-in already exists
        existing_checkin = CheckIn.query.filter_by(ticket_id=ticket.ticket_id).first()
        if existing_checkin:
            return jsonify({'error': 'Ticket already checked in'}), 400
        
        check_in = CheckIn(
            ticket_id=ticket.ticket_id,
            event_id=event.event_id,
            check_in_method=data.get('check_in_method', 'qr_scan'),
            checked_in_by=user_id,
            location=data.get('location')
        )
        
        db.session.add(check_in)
        
        # Update ticket status (simulating trigger)
        ticket.status = 'used'
        ticket.checked_in_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Check-in successful',
            'check_in': check_in.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@checkins_bp.route('/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event_check_ins(event_id):
    """Get all check-ins for an event"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Only organizer/admin can view check-ins
        if user.user_type != 'admin' and event.organizer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        check_ins = CheckIn.query.filter_by(event_id=event_id).all()
        
        check_ins_list = []
        for check_in in check_ins:
            check_in_dict = check_in.to_dict()
            check_in_dict['ticket'] = check_in.ticket.to_dict() if check_in.ticket else None
            check_in_dict['checked_in_by_user'] = check_in.checked_in_by_user.to_dict() if check_in.checked_in_by_user else None
            check_ins_list.append(check_in_dict)
        
        return jsonify(check_ins_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@checkins_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket_check_in(ticket_id):
    """Get check-in record for a ticket"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Check authorization
        if user.user_type != 'admin' and ticket.order.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        check_in = CheckIn.query.filter_by(ticket_id=ticket_id).first()
        
        if not check_in:
            return jsonify({'error': 'Check-in not found'}), 404
        
        check_in_dict = check_in.to_dict()
        check_in_dict['ticket'] = ticket.to_dict()
        check_in_dict['event'] = check_in.event.to_dict() if check_in.event else None
        
        return jsonify(check_in_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

