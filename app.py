from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db
from utils.email_service import mail
import os

# Import blueprints
from routes.auth import auth_bp
from routes.venues import venues_bp
from routes.events import events_bp
from routes.orders import orders_bp
from routes.tickets import tickets_bp
from routes.promo_codes import promo_codes_bp
from routes.seating import seating_bp
from routes.checkins import checkins_bp
from routes.payments import payments_bp
from routes.views import views_bp

def create_app(config_name='default'):
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(venues_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(promo_codes_bp)
    app.register_blueprint(seating_bp)
    app.register_blueprint(checkins_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(views_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Event Management API is running'
        }), 200
    
    # API Root endpoint (for API clients)
    @app.route('/api', methods=['GET'])
    def api_root():
        return jsonify({
            'message': 'Event Management and Ticketing Platform API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'venues': '/api/venues',
                'events': '/api/events',
                'orders': '/api/orders',
                'tickets': '/api/tickets',
                'promo_codes': '/api/promo-codes',
                'seating': '/api/seating',
                'check_ins': '/api/check-ins',
                'payments': '/api/payments'
            }
        }), 200
    
    # Create uploads directory if it doesn't exist
    with app.app_context():
        # Ensure 'credits' column exists on users table (simple migration)
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('users')]
            if 'credits' not in cols:
                # Add credits column with default 500.00
                db.engine.execute(text("ALTER TABLE users ADD COLUMN credits DECIMAL(10,2) NOT NULL DEFAULT 500.00"))
                print("[OK] Added 'credits' column to users table with default 500.00")
            # Remove qr_code column from tickets if present (no longer stored)
            ticket_cols = [c['name'] for c in inspector.get_columns('tickets')]
            if 'qr_code' in ticket_cols:
                try:
                    db.engine.execute(text("ALTER TABLE tickets DROP COLUMN qr_code"))
                    print("[OK] Dropped 'tickets.qr_code' column")
                except Exception as e_drop:
                    print(f"[WARNING] Could not drop tickets.qr_code: {str(e_drop)}")
        except Exception as e:
            print(f"[WARNING] Could not ensure 'credits' column: {str(e)}")
        
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        # Resolve to absolute path - use the directory where app.py is located
        # app.root_path might point to the package directory, so use the parent
        if not os.path.isabs(upload_folder):
            # Get the directory containing this file (app.py)
            app_dir = os.path.dirname(os.path.abspath(__file__))
            upload_folder = os.path.join(app_dir, upload_folder)
        upload_folder = os.path.abspath(upload_folder)
        banner_folder = os.path.join(upload_folder, 'banners')
        
        # Create directories
        try:
            os.makedirs(banner_folder, exist_ok=True)
            print(f"[OK] Upload folder created: {upload_folder}")
            print(f"[OK] Banner folder created: {banner_folder}")
        except Exception as e:
            print(f"[WARNING] Failed to create upload directories: {str(e)}")
        
        # Update config with absolute path for consistency
        app.config['UPLOAD_FOLDER'] = upload_folder
        
        # Create database tables
        try:
            # Test database connection
            db.engine.connect()
            print("[OK] Database connection established")
            
            # Create tables
            db.create_all()
            print("[OK] Database tables initialized")
        except Exception as e:
            print(f"[WARNING] Database connection warning: {str(e)}")
            print("[WARNING] Make sure MySQL is running and database is created")
            print("[WARNING] Run 'python test_db_connection.py' to diagnose issues")
    
    # Serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files"""
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        # Should already be absolute from app initialization, but handle both cases
        if os.path.isabs(upload_folder):
            directory = upload_folder
        else:
            directory = os.path.join(app.root_path, upload_folder)
            directory = os.path.abspath(directory)
        return send_from_directory(directory, filename)
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)

