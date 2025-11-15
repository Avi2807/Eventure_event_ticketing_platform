from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Ticket, User, Order
from utils.qr_generator import generate_ticket_qr_code

tickets_bp = Blueprint('tickets', __name__, url_prefix='/api/tickets')

@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    """Get ticket by ID"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        order = ticket.order
        
        # Check authorization
        if user.user_type != 'admin' and order.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        ticket_dict = ticket.to_dict()
        ticket_dict['order'] = order.to_dict() if order else None
        ticket_dict['ticket_type'] = ticket.ticket_type.to_dict() if ticket.ticket_type else None
        ticket_dict['seat'] = ticket.seat.to_dict() if ticket.seat else None
        ticket_dict['event'] = order.event.to_dict() if order and order.event else None
        
        return jsonify(ticket_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/<int:ticket_id>/qr', methods=['GET'])
@jwt_required()
def get_ticket_qr(ticket_id):
    """Get QR code for ticket"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        order = ticket.order
        
        # Check authorization
        if user.user_type != 'admin' and order.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        qr_code = generate_ticket_qr_code(ticket.ticket_number, ticket.ticket_id)
        
        return jsonify({
            'ticket_id': ticket.ticket_id,
            'ticket_number': ticket.ticket_number,
            'qr_code': qr_code
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/validate/<ticket_number>', methods=['GET'])
@jwt_required()
def validate_ticket(ticket_number):
    """Validate a ticket by ticket number (for check-in)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Only staff/admin can validate tickets
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        ticket = Ticket.query.filter_by(ticket_number=ticket_number).first()
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        ticket_dict = ticket.to_dict()
        ticket_dict['order'] = ticket.order.to_dict() if ticket.order else None
        ticket_dict['event'] = ticket.order.event.to_dict() if ticket.order and ticket.order.event else None
        
        return jsonify({
            'valid': ticket.status == 'valid',
            'ticket': ticket_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

