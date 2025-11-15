from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, User, Ticket, TicketType, Event
from utils.order_generator import create_order
from utils.email_service import send_order_confirmation

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_new_order():
    """Create a new order"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # 1) Only attendees can purchase
        if user.user_type != 'attendee':
            return jsonify({'error': 'Only attendees can purchase tickets'}), 403
        data = request.get_json()
        
        required_fields = ['event_id', 'ticket_items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Coerce event_id to int (frontend may send string)
        try:
            event_id = int(data['event_id'])
        except Exception:
            return jsonify({'error': 'Invalid event_id'}), 400
        
        # Check if event exists and is not cancelled
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        if event.status == 'cancelled':
            return jsonify({'error': 'Cannot purchase tickets for a cancelled event'}), 400
        if event.status == 'completed':
            return jsonify({'error': 'Cannot purchase tickets for a completed event'}), 400
        
        # Normalize ticket_items ids
        ticket_items = data['ticket_items']
        for item in ticket_items:
            try:
                item['ticket_type_id'] = int(item['ticket_type_id'])
            except Exception:
                return jsonify({'error': 'Invalid ticket_type_id'}), 400
        
        success, message, order = create_order(
            user_id=user_id,
            event_id=event_id,
            ticket_items=ticket_items,
            promo_code=data.get('promo_code'),
            payment_method=data.get('payment_method', 'credit_card')
        )
        
        if not success:
            return jsonify({'error': message}), 400
        
        order_dict = order.to_dict()
        order_dict['tickets'] = [ticket.to_dict() for ticket in order.tickets]
        
        # Include updated user credits
        user = User.query.get(user_id)
        return jsonify({
            'message': 'Order created successfully',
            'order': order_dict,
            'user': user.to_dict() if user else None
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get user's orders"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Admin can see all orders
        if user.user_type == 'admin':
            orders = Order.query.all()
        else:
            orders = Order.query.filter_by(user_id=user_id).all()
        
        orders_list = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['event'] = order.event.to_dict() if order.event else None
            order_dict['ticket_count'] = len(order.tickets)
            orders_list.append(order_dict)
        
        return jsonify(orders_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get order by ID"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check authorization
        if user.user_type != 'admin' and order.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        order_dict = order.to_dict()
        order_dict['event'] = order.event.to_dict() if order.event else None
        order_dict['tickets'] = [ticket.to_dict() for ticket in order.tickets]
        order_dict['payments'] = [payment.to_dict() for payment in order.payments]
        
        return jsonify(order_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/tickets', methods=['GET'])
@jwt_required()
def get_order_tickets(order_id):
    """Get tickets for an order"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check authorization
        if user.user_type != 'admin' and order.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        tickets = Ticket.query.filter_by(order_id=order_id).all()
        
        tickets_list = []
        for ticket in tickets:
            ticket_dict = ticket.to_dict()
            ticket_dict['ticket_type'] = ticket.ticket_type.to_dict() if ticket.ticket_type else None
            ticket_dict['seat'] = ticket.seat.to_dict() if ticket.seat else None
            tickets_list.append(ticket_dict)
        
        return jsonify(tickets_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

