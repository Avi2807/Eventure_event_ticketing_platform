from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Event, User, Venue, TicketType, EventAnalytics, Order, Payment, Ticket, Refund
from datetime import datetime
from sqlalchemy import or_
import os
import uuid
from werkzeug.utils import secure_filename
from utils.payment_processor import process_refund
from utils.email_service import send_event_cancelled

events_bp = Blueprint('events', __name__, url_prefix='/api/events')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@events_bp.route('', methods=['GET'])
def get_events():
    """Get all events with optional filters"""
    try:
        status = request.args.get('status')
        category = request.args.get('category')
        city = request.args.get('city')
        search = request.args.get('search')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Event.query
        
        if status:
            query = query.filter(Event.status == status)
        if category:
            query = query.filter(Event.category == category)
        if city:
            query = query.join(Venue).filter(Venue.city.ilike(f'%{city}%'))
        if search:
            query = query.filter(
                or_(
                    Event.event_name.ilike(f'%{search}%'),
                    Event.description.ilike(f'%{search}%')
                )
            )
        if start_date:
            query = query.filter(Event.start_datetime >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Event.start_datetime <= datetime.fromisoformat(end_date))
        
        events = query.all()
        
        # Include venue information for each event
        events_list = []
        for event in events:
            event_dict = event.to_dict()
            event_dict['venue'] = event.venue.to_dict() if event.venue else None
            events_list.append(event_dict)
        
        return jsonify(events_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get event by ID with details"""
    try:
        event = Event.query.get(event_id)
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        event_dict = event.to_dict()
        event_dict['venue'] = event.venue.to_dict() if event.venue else None
        event_dict['organizer'] = event.organizer.to_dict() if event.organizer else None
        event_dict['ticket_types'] = [tt.to_dict() for tt in event.ticket_types]
        
        # Get analytics if available
        if event.event_analytics:
            event_dict['analytics'] = event.event_analytics.to_dict()
        
        return jsonify(event_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event (organizer/admin only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized. Only organizers and admins can create events.'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['venue_id', 'event_name', 'start_datetime', 'end_datetime']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify venue exists
        venue = Venue.query.get(data['venue_id'])
        if not venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        # Parse datetime strings - handle ISO format
        try:
            start_dt_str = str(data['start_datetime'])
            end_dt_str = str(data['end_datetime'])
            
            # Parse ISO datetime strings from JavaScript toISOString()
            # Format is typically: "2024-11-10T16:00:00.000Z"
            from datetime import timezone
            
            def parse_datetime(dt_str):
                """Parse ISO datetime string and return naive UTC datetime"""
                # Remove 'Z' and replace with '+00:00' for fromisoformat
                if dt_str.endswith('Z'):
                    # Format: "2024-11-10T16:00:00.000Z"
                    dt_str = dt_str[:-1] + '+00:00'
                    dt = datetime.fromisoformat(dt_str)
                elif '+' in dt_str or dt_str.count('-') >= 4:
                    # Has timezone: "2024-11-10T16:00:00+00:00"
                    dt = datetime.fromisoformat(dt_str)
                else:
                    # Naive datetime: "2024-11-10T16:00:00" or "2024-11-10T16:00"
                    # Try parsing with strptime
                    if '.' in dt_str:
                        # Has milliseconds, remove them
                        dt_str = dt_str.split('.')[0]
                    
                    if dt_str.count(':') == 2:
                        # Has seconds
                        dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
                    else:
                        # No seconds
                        dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M')
                    
                    # Assume UTC
                    dt = dt.replace(tzinfo=timezone.utc)
                
                # Convert to UTC and make naive for database storage
                if dt.tzinfo:
                    dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                return dt
            
            start_datetime = parse_datetime(start_dt_str)
            end_datetime = parse_datetime(end_dt_str)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error parsing datetime: {str(e)}")
            print(f"Received start_datetime: {data.get('start_datetime')}")
            print(f"Received end_datetime: {data.get('end_datetime')}")
            print(f"Traceback: {error_trace}")
            return jsonify({
                'error': f'Invalid datetime format: {str(e)}',
                'received_start': data.get('start_datetime'),
                'received_end': data.get('end_datetime'),
                'details': error_trace if current_app.config.get('DEBUG') else None
            }), 400
        
        # Validate that end datetime is after start datetime
        if end_datetime <= start_datetime:
            return jsonify({'error': 'End datetime must be after start datetime'}), 400
        
        event = Event(
            organizer_id=user_id,
            venue_id=data['venue_id'],
            event_name=data['event_name'],
            description=data.get('description') or None,
            category=data.get('category') or None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status=data.get('status', 'draft'),
            banner_image=data.get('banner_image') or None
        )
        
        db.session.add(event)
        db.session.flush()
        
        # Create analytics record (only if event was created successfully)
        # Check if analytics already exists (shouldn't happen for new events, but be safe)
        existing_analytics = EventAnalytics.query.filter_by(event_id=event.event_id).first()
        if not existing_analytics:
            analytics = EventAnalytics(event_id=event.event_id)
            db.session.add(analytics)
        else:
            print(f"Warning: Analytics record already exists for event {event.event_id}")
        
        # Commit event and analytics together
        db.session.commit()
        
        return jsonify({
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error creating event: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({'error': str(e), 'details': error_trace if current_app.config.get('DEBUG') else None}), 500

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update an event (organizer/admin only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        if user.user_type != 'admin' and event.organizer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'event_name' in data:
            event.event_name = data['event_name']
        if 'description' in data:
            event.description = data['description']
        if 'category' in data:
            event.category = data['category']
        if 'start_datetime' in data:
            event.start_datetime = datetime.fromisoformat(data['start_datetime'].replace('Z', '+00:00'))
        if 'end_datetime' in data:
            event.end_datetime = datetime.fromisoformat(data['end_datetime'].replace('Z', '+00:00'))
        if 'status' in data:
            event.status = data['status']
        if 'banner_image' in data:
            event.banner_image = data['banner_image']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Event updated successfully',
            'event': event.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>/ticket-types', methods=['GET'])
def get_ticket_types(event_id):
    """Get all ticket types for an event"""
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        ticket_types = TicketType.query.filter_by(event_id=event_id).all()
        return jsonify([tt.to_dict() for tt in ticket_types]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>/ticket-types', methods=['POST'])
@jwt_required()
def create_ticket_type(event_id):
    """Create a ticket type for an event"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        if user.user_type != 'admin' and event.organizer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        required_fields = ['type_name', 'price', 'quantity_total', 'sale_start', 'sale_end']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        ticket_type = TicketType(
            event_id=event_id,
            section_id=data.get('section_id'),
            type_name=data['type_name'],
            description=data.get('description'),
            price=data['price'],
            quantity_total=data['quantity_total'],
            quantity_available=data['quantity_total'],
            sale_start=datetime.fromisoformat(data['sale_start'].replace('Z', '+00:00')),
            sale_end=datetime.fromisoformat(data['sale_end'].replace('Z', '+00:00')),
            min_purchase=data.get('min_purchase', 1),
            max_purchase=data.get('max_purchase', 10)
        )
        
        db.session.add(ticket_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket type created successfully',
            'ticket_type': ticket_type.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>/ticket-types/<int:ticket_type_id>', methods=['PUT'])
@jwt_required()
def update_ticket_type(event_id, ticket_type_id):
    """Update a ticket type for an event"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        if user.user_type != 'admin' and event.organizer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        ticket_type = TicketType.query.filter_by(event_id=event_id, ticket_type_id=ticket_type_id).first()
        if not ticket_type:
            return jsonify({'error': 'Ticket type not found'}), 404
        
        data = request.get_json()
        
        if 'type_name' in data:
            ticket_type.type_name = data['type_name']
        if 'description' in data:
            ticket_type.description = data['description']
        if 'price' in data:
            ticket_type.price = data['price']
        if 'quantity_total' in data:
            # Adjust quantity_available if total quantity changes
            old_total = ticket_type.quantity_total
            new_total = data['quantity_total']
            ticket_type.quantity_total = new_total
            # If increasing total, add to available. If decreasing, don't go below sold count
            sold_count = old_total - ticket_type.quantity_available
            ticket_type.quantity_available = max(0, new_total - sold_count)
        if 'sale_start' in data:
            ticket_type.sale_start = datetime.fromisoformat(data['sale_start'].replace('Z', '+00:00'))
        if 'sale_end' in data:
            ticket_type.sale_end = datetime.fromisoformat(data['sale_end'].replace('Z', '+00:00'))
        if 'min_purchase' in data:
            ticket_type.min_purchase = data['min_purchase']
        if 'max_purchase' in data:
            ticket_type.max_purchase = data['max_purchase']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket type updated successfully',
            'ticket_type': ticket_type.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>/ticket-types/<int:ticket_type_id>', methods=['DELETE'])
@jwt_required()
def delete_ticket_type(event_id, ticket_type_id):
    """Delete a ticket type for an event"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        if user.user_type != 'admin' and event.organizer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        ticket_type = TicketType.query.filter_by(event_id=event_id, ticket_type_id=ticket_type_id).first()
        if not ticket_type:
            return jsonify({'error': 'Ticket type not found'}), 404
        
        # Check if any tickets have been sold for this type
        tickets_sold = Ticket.query.filter_by(ticket_type_id=ticket_type_id).count()
        if tickets_sold > 0:
            return jsonify({'error': f'Cannot delete ticket type. {tickets_sold} ticket(s) have already been sold.'}), 400
        
        db.session.delete(ticket_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket type deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>/analytics', methods=['GET'])
@jwt_required()
def get_event_analytics(event_id):
    """Get event analytics (organizer/admin only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        if user.user_type != 'admin' and event.organizer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        analytics = event.event_analytics
        if not analytics:
            # Backfill a default analytics row for legacy events
            analytics = EventAnalytics(
                event_id=event.event_id,
                total_tickets_sold=0,
                total_revenue=0.00,
                total_attendees=0,
                tickets_by_type={},
                revenue_by_type={}
            )
            db.session.add(analytics)
            db.session.commit()
        
        return jsonify(analytics.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/upload-banner', methods=['POST'])
@jwt_required()
def upload_banner():
    """Upload banner image for event"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.user_type not in ['admin', 'organizer']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if file is present
        if 'banner' not in request.files:
            return jsonify({'error': 'No file provided. Make sure the file input name is "banner".'}), 400
        
        file = request.files['banner']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed types: PNG, JPG, JPEG, GIF, WEBP'}), 400
        
        # Get upload folder from config (should be absolute path set by app.py)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # If it's already absolute (set by app.py), use it directly
        if not os.path.isabs(upload_folder):
            # Fallback: resolve relative to app root
            app_dir = os.path.dirname(os.path.abspath(current_app.root_path))
            upload_folder = os.path.join(app_dir, upload_folder)
        
        upload_folder = os.path.abspath(upload_folder)
        banner_folder = os.path.join(upload_folder, 'banners')
        
        # Debug logging (remove in production)
        if current_app.config.get('DEBUG'):
            print(f"[DEBUG] Upload folder: {upload_folder}")
            print(f"[DEBUG] Banner folder: {banner_folder}")
        
        # Create directories if they don't exist
        try:
            os.makedirs(banner_folder, exist_ok=True)
        except Exception as e:
            return jsonify({'error': f'Failed to create upload directory: {str(e)}'}), 500
        
        # Generate unique filename
        try:
            filename = secure_filename(file.filename)
            if '.' not in filename:
                return jsonify({'error': 'File must have an extension'}), 400
            file_ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
            file_path = os.path.join(banner_folder, unique_filename)
        except Exception as e:
            return jsonify({'error': f'Failed to process filename: {str(e)}'}), 500
        
        # Save file
        try:
            file.save(file_path)
            # Verify file was saved
            if not os.path.exists(file_path):
                return jsonify({'error': 'File was not saved successfully'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
        
        # Return URL path (relative to root)
        banner_url = f"/uploads/banners/{unique_filename}"
        
        return jsonify({
            'message': 'Banner uploaded successfully',
            'banner_url': banner_url
        }), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error uploading banner: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({
            'error': str(e),
            'details': error_trace if current_app.config.get('DEBUG') else None
        }), 500

@events_bp.route('/<int:event_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_event(event_id):
    """Cancel an event and refund all ticket buyers (organizer/admin only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check authorization - only organizer or admin can cancel
        if user.user_type != 'admin' and event.organizer_id != user_id:
            return jsonify({'error': 'Unauthorized. Only the event organizer or admin can cancel events.'}), 403
        
        # Check if event is already cancelled
        if event.status == 'cancelled':
            return jsonify({'error': 'Event is already cancelled'}), 400
        
        # Check if event is already completed
        if event.status == 'completed':
            return jsonify({'error': 'Cannot cancel a completed event'}), 400
        
        # Get all completed orders for this event
        orders = Order.query.filter_by(event_id=event_id, status='completed').all()
        
        refunded_orders = []
        refund_errors = []
        
        # Process refunds for each order in a single transaction
        for order in orders:
            try:
                # Get the payment for this order
                payment = Payment.query.filter_by(order_id=order.order_id, status='completed').first()
                
                if not payment:
                    refund_errors.append(f"Order {order.order_number}: No completed payment found")
                    continue
                
                # Skip if payment is already refunded
                if payment.status == 'refunded':
                    refund_errors.append(f"Order {order.order_number}: Payment already refunded")
                    continue
                
                refund_amount = float(order.total_amount)
                
                # Get the user to refund credits
                order_user = User.query.get(order.user_id)
                if not order_user:
                    refund_errors.append(f"Order {order.order_number}: User not found")
                    continue
                
                # Create refund record
                refund = Refund(
                    payment_id=payment.payment_id,
                    amount=refund_amount,
                    reason=f"Event cancelled: {event.event_name}",
                    status='completed',
                    processed_at=datetime.utcnow()
                )
                db.session.add(refund)
                
                # Update payment status
                payment.status = 'refunded'
                
                # Refund credits to user account
                user_credits = float(order_user.credits or 0.0)
                order_user.credits = user_credits + refund_amount
                
                # Update order status
                order.status = 'refunded'
                
                # Update all tickets for this order to refunded status
                tickets = Ticket.query.filter_by(order_id=order.order_id).all()
                for ticket in tickets:
                    if ticket.status != 'refunded':
                        ticket.status = 'refunded'
                        # Link refund to first ticket if not already linked
                        if not refund.ticket_id:
                            refund.ticket_id = ticket.ticket_id
                
                refunded_orders.append({
                    'order_id': order.order_id,
                    'order_number': order.order_number,
                    'refund_amount': refund_amount
                })
                
            except Exception as e:
                refund_errors.append(f"Order {order.order_number}: {str(e)}")
                current_app.logger.error(f"Error processing refund for order {order.order_id}: {str(e)}")
                continue
        
        # Update event status to cancelled
        event.status = 'cancelled'
        
        # Commit all changes
        db.session.commit()
        
        # Send cancellation emails to all ticket holders
        try:
            send_event_cancelled(event_id)
        except Exception as e:
            current_app.logger.error(f"Error sending cancellation emails: {str(e)}")
            # Don't fail the cancellation if email fails
        
        return jsonify({
            'message': 'Event cancelled successfully',
            'event': event.to_dict(),
            'refunded_orders_count': len(refunded_orders),
            'refunded_orders': refunded_orders,
            'refund_errors': refund_errors if refund_errors else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Error cancelling event: {str(e)}")
        current_app.logger.error(f"Traceback: {error_trace}")
        return jsonify({
            'error': str(e),
            'details': error_trace if current_app.config.get('DEBUG') else None
        }), 500

