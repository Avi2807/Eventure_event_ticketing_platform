"""
Fix users table - add missing date_of_birth column
"""
import pymysql

try:
    print("Connecting to database...")
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='avi1234',
        database='event_management_db',
        charset='utf8mb4'
    )
    
    print("✓ Connected to database EM")
    
    with connection.cursor() as cursor:
        # Check if date_of_birth column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'date_of_birth'")
        result = cursor.fetchone()
        
        if result:
            print("✓ Column 'date_of_birth' already exists")
        else:
            print("Adding missing 'date_of_birth' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth DATE AFTER phone")
            print("✓ Column 'date_of_birth' added successfully")
        
        # Verify all columns
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        print("\nUsers table structure:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
    
    connection.commit()
    connection.close()
    print("\n✓ Users table fixed successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")


