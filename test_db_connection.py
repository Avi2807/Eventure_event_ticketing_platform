"""
Database Connection Test Script
Run this script to test your database connectivity before running the main application
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DatabaseError
from config import config

def test_database_connection():
    """Test database connection"""
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    
    # Get database URI from config
    app_config = config['development']
    database_uri = app_config.SQLALCHEMY_DATABASE_URI
    
    print(f"\nDatabase URI: {database_uri.replace(database_uri.split('@')[0].split('//')[1] if '@' in database_uri else '', '***@***') if '@' in database_uri else database_uri}")
    print("\nAttempting to connect...")
    
    try:
        # Create engine
        engine = create_engine(database_uri, echo=False)
        
        # Test connection
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            print("✓ Database connection successful!")
            
            # Test database exists
            result = connection.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            if db_name:
                print(f"✓ Connected to database: {db_name}")
            else:
                print("⚠ Warning: No database selected")
            
            # Test MySQL version
            try:
                result = connection.execute(text("SELECT VERSION()"))
                version = result.fetchone()[0]
                print(f"✓ MySQL Version: {version}")
            except Exception:
                print("⚠ Could not retrieve MySQL version")
            
            # Check if tables exist
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """))
            table_count = result.fetchone()[0]
            print(f"✓ Tables in database: {table_count}")
            
            if table_count == 0:
                print("\n⚠ No tables found. Run 'python init_db.py' to create tables.")
            else:
                print("\n✓ Database is ready to use!")
            
            return True
            
    except OperationalError as e:
        print(f"\n✗ Connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if MySQL server is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure the database exists (CREATE DATABASE event_management_db;)")
        print("4. Check if PyMySQL is installed: pip install PyMySQL")
        return False
        
    except DatabaseError as e:
        print(f"\n✗ Database error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check database permissions")
        print("2. Verify database name is correct")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_pymysql_installation():
    """Test if PyMySQL is installed"""
    try:
        import pymysql
        print("✓ PyMySQL is installed")
        return True
    except ImportError:
        print("✗ PyMySQL is not installed")
        print("  Install it with: pip install PyMySQL")
        return False

if __name__ == '__main__':
    print("\nTesting database connectivity...\n")
    
    # Test PyMySQL installation first
    if not test_pymysql_installation():
        print("\nPlease install PyMySQL first before testing connection.")
        sys.exit(1)
    
    print()
    
    # Test database connection
    success = test_database_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed! Database is ready.")
        sys.exit(0)
    else:
        print("✗ Connection test failed. Please fix the issues above.")
        sys.exit(1)

