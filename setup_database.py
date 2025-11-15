"""
Database Setup Script
This script helps you set up your MySQL database for the Event Management Platform
"""
import mysql.connector
from mysql.connector import Error
import sys

def create_database():
    """Create the database if it doesn't exist"""
    print("=" * 60)
    print("MySQL Database Setup for Event Management Platform")
    print("=" * 60)
    
    # Get database credentials
    print("\nPlease enter your MySQL credentials:")
    host = input("Host (default: localhost): ").strip() or "localhost"
    port = input("Port (default: 3306): ").strip() or "3306"
    user = input("Username (default: root): ").strip() or "root"
    password = input("Password: ").strip()
    database_name = input("Database name (default: event_management_db): ").strip() or "event_management_db"
    
    try:
        # Connect to MySQL server (without specifying database)
        print(f"\nConnecting to MySQL server at {host}:{pCREATE VIEW event_sales_summary AS
SELECT 
    e.event_id,
    e.event_name,
    e.start_datetime,
    e.status as event_status,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(t.ticket_id) as tickets_sold,
    SUM(o.total_amount) as total_revenue,
    COUNT(DISTINCT CASE WHEN t.status = 'used' THEN t.ticket_id END) as attendees_checked_in
FROM events e
LEFT JOIN orders o ON e.event_id = o.event_id AND o.status = 'completed'
LEFT JOIN tickets t ON o.order_id = t.order_id
GROUP BY e.event_id, e.event_name, e.start_datetime, e.status;

-- View: Available Tickets
CREATE VIEW available_tickets AS
SELECT 
    tt.ticket_type_id,
    tt.event_id,
    e.event_name,
    tt.type_name,
    tt.price,
    tt.quantity_available,
    tt.sale_start,
    tt.sale_end,
    CASE 
        WHEN NOW() < tt.sale_start THEN 'not_started'
        WHEN NOW() > tt.sale_end THEN 'ended'
        WHEN tt.quantity_available = 0 THEN 'sold_out'
        ELSE 'available'
    END as availability_status
FROM ticket_types tt
JOIN events e ON tt.event_id = e.event_id
WHERE e.status = 'published';

-- View: User Order History
CREATE VIEW user_order_history AS
SELECT 
    o.order_id,
    o.user_id,
    u.email,
    u.first_name,
    u.last_name,
    o.order_number,
    o.event_id,
    e.event_name,
    e.start_datetime,
    o.total_amount,
    o.status as order_status,
    o.created_at as order_date,
    COUNT(t.ticket_id) as ticket_count
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN events e ON o.event_id = e.event_id
LEFT JOIN tickets t ON o.order_id = t.order_id
GROUP BY o.order_id, o.user_id, u.email, u.first_name, u.last_name, 
         o.order_number, o.event_id, e.event_name, e.start_datetime, 
         o.total_amount, o.status, o.created_at;

-- ============================================
-- SAMPLE INDEXES FOR PERFORMANCE
-- ============================================

-- Composite indexes for common query patterns
CREATE INDEX idx_event_date_status ON events(start_datetime, status);
CREATE INDEX idx_ticket_order_status ON tickets(order_id, status);
CREATE INDEX idx_order_user_event ON orders(user_id, event_id, created_at);

-- Full-text search indexes
ALTER TABLE events ADD FULLTEXT INDEX ft_event_search (event_name, description);
ALTER TABLE venues ADD FULLTEXT INDEX ft_venue_search (venue_name, city, description);ort}...")
        connection = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password
        )
        
        if connection.is_connected():
            print("✓ Successfully connected to MySQL server")
            
            cursor = connection.cursor()
            
            # Check if database exists
            cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
            result = cursor.fetchone()
            
            if result:
                print(f"⚠ Database '{database_name}' already exists")
                response = input(f"Do you want to drop and recreate it? (yes/no): ").strip().lower()
                if response == 'yes':
                    cursor.execute(f"DROP DATABASE {database_name}")
                    print(f"✓ Dropped existing database '{database_name}'")
                else:
                    print(f"✓ Using existing database '{database_name}'")
                    cursor.close()
                    connection.close()
                    return host, port, user, password, database_name
            
            # Create database
            print(f"\nCreating database '{database_name}'...")
            cursor.execute(f"CREATE DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✓ Database '{database_name}' created successfully")
            
            cursor.close()
            connection.close()
            
            print("\n" + "=" * 60)
            print("✓ Database setup complete!")
            print("=" * 60)
            print(f"\nDatabase connection string:")
            print(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}")
            print("\nUpdate your .env file with this connection string:")
            print(f"DATABASE_URI=mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}")
            print("\nNext steps:")
            print("1. Update the DATABASE_URI in your .env file")
            print("2. Run: python init_db.py (to create tables)")
            print("3. Run: python app.py (to start the application)")
            
            return host, port, user, password, database_name
            
    except Error as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check your username and password")
        print("3. Verify MySQL is installed and accessible")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        import mysql.connector
    except ImportError:
        print("✗ mysql-connector-python is not installed")
        print("Install it with: pip install mysql-connector-python")
        sys.exit(1)
    
    create_database()


