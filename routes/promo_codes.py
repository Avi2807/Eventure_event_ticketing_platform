from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, PromotionalCode, User, Event
from datetime import datetime

promo_codes_bp = Blueprint('promo_codes', __name__, url_prefix='/api/promo-codes')

@promo_codes_bp.route('', methods=['POST'])
@jwt_required()
def create_promo_code():
    """Create a promotional code (organizer/admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        required_fields = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_until']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if code already exists
        if PromotionalCode.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Promotional code already exists'}), 400
        
        # Validate event if provided
        if data.get('event_id'):
            event = Event.query.get(data['event_id'])
            if not event:
                return jsonify({'error': 'Event not found'}), 404
            
            if user.user_type != 'admin' and event.organizer_id != user_id:
                return jsonify({'error': 'Unauthorized to create promo for this event'}), 403
        
        promo_code = PromotionalCode(
            event_id=data.get('event_id'),
            code=data['code'],
            discount_type=data['discount_type'],
            discount_value=data['discount_value'],
            usage_limit=data.get('usage_limit'),
            valid_from=datetime.fromisoformat(data['valid_from'].replace('Z', '+00:00')),
            valid_until=datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00')),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(promo_code)
        db.session.commit()
        
        return jsonify({
            'message': 'Promotional code created successfully',
            'promo_code': promo_code.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@promo_codes_bp.route('/validate', methods=['POST'])
def validate_promo_code():
    """Validate a promotional code"""
    try:
        data = request.get_json()
        
        if 'code' not in data:
            return jsonify({'error': 'Code is required'}), 400
        
        promo_code = PromotionalCode.query.filter_by(code=data['code']).first()
        
        if not promo_code:
            return jsonify({
                'valid': False,
                'message': 'Promotional code not found'
            }), 200
        
        is_valid, message = promo_code.is_valid()
        
        return jsonify({
            'valid': is_valid,
            'message': message,
            'promo_code': promo_code.to_dict() if is_valid else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@promo_codes_bp.route('', methods=['GET'])
def get_promo_codes():
    """Get promotional codes"""
    try:
        event_id = request.args.get('event_id', type=int)
        is_active = request.args.get('is_active', type=bool)
        
        query = PromotionalCode.query
        
        if event_id:
            query = query.filter(PromotionalCode.event_id == event_id)
        if is_active is not None:
            query = query.filter(PromotionalCode.is_active == is_active)
        
        promo_codes = query.all()
        
        return jsonify([promo.to_dict() for promo in promo_codes]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@promo_codes_bp.route('/<int:promo_id>', methods=['GET'])
def get_promo_code(promo_id):
    """Get promotional code by ID"""
    try:
        promo_code = PromotionalCode.query.get(promo_id)
        
        if not promo_code:
            return jsonify({'error': 'Promotional code not found'}), 404
        
        return jsonify(promo_code.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@promo_codes_bp.route('/<int:promo_id>', methods=['PUT'])
@jwt_required()
def update_promo_code(promo_id):
    """Update promotional code (organizer/admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        promo_code = PromotionalCode.query.get(promo_id)
        if not promo_code:
            return jsonify({'error': 'Promotional code not found'}), 404
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if promo_code.event_id and user.user_type != 'admin':
            event = Event.query.get(promo_code.event_id)
            if event.organizer_id != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'discount_value' in data:
            promo_code.discount_value = data['discount_value']
        if 'usage_limit' in data:
            promo_code.usage_limit = data['usage_limit']
        if 'valid_from' in data:
            promo_code.valid_from = datetime.fromisoformat(data['valid_from'].replace('Z', '+00:00'))
        if 'valid_until' in data:
            promo_code.valid_until = datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00'))
        if 'is_active' in data:
            promo_code.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Promotional code updated successfully',
            'promo_code': promo_code.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

