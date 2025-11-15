"""
Database initialization script
Run this script to create all database tables
"""
from app import create_app
from models import db
from sqlalchemy.exc import OperationalError

app = create_app('development')

with app.app_context():
    try:
        # Test connection first
        print("Testing database connection...")
        db.engine.connect()
        print("✓ Database connection successful")
        
        print("\nCreating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n✓ Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
        
        print("\n✓ Database initialization complete!")
        print("\nYou can now run the Flask app with: python app.py")
        
    except OperationalError as e:
        print(f"\n✗ Database connection failed: {str(e)}")
        print("\nPlease:")
        print("1. Ensure MySQL server is running")
        print("2. Create the database: CREATE DATABASE event_management_db;")
        print("3. Update DATABASE_URI in .env file with correct credentials")
        print("4. Run 'python test_db_connection.py' to diagnose issues")
        exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        exit(1)

