from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Payment, Order, User, Refund
from utils.payment_processor import process_payment, process_refund
from utils.email_service import send_refund_processed

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@payments_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_payments(order_id):
    """Get payments for an order"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check authorization
        if user.user_type != 'admin' and order.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        payments = Payment.query.filter_by(order_id=order_id).all()
        
        return jsonify([payment.to_dict() for payment in payments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment by ID"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        order = payment.order
        
        # Check authorization
        if user.user_type != 'admin' and order.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        payment_dict = payment.to_dict()
        payment_dict['order'] = order.to_dict() if order else None
        
        return jsonify(payment_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:payment_id>/refund', methods=['POST'])
@jwt_required()
def create_refund(payment_id):
    """Create a refund for a payment (admin/organizer only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        data = request.get_json()
        
        amount = data.get('amount', float(payment.amount))
        reason = data.get('reason')
        
        success, message, refund = process_refund(payment_id, amount, reason)
        
        if not success:
            return jsonify({'error': message}), 400
        
        # Send refund email
        send_refund_processed(refund.refund_id)
        
        return jsonify({
            'message': 'Refund processed successfully',
            'refund': refund.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/refunds', methods=['GET'])
@jwt_required()
def get_refunds():
    """Get refunds (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.user_type != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        refunds = Refund.query.all()
        
        refunds_list = []
        for refund in refunds:
            refund_dict = refund.to_dict()
            refund_dict['payment'] = refund.payment.to_dict() if refund.payment else None
            refund_dict['ticket'] = refund.ticket.to_dict() if refund.ticket else None
            refunds_list.append(refund_dict)
        
        return jsonify(refunds_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

