"""
Create Database EM with the specified credentials
"""
import pymysql

try:
    # Connect to MySQL server (without specifying database)
    print("Connecting to MySQL server...")
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Shash@123',
        charset='utf8mb4'
    )
    
    print("✓ Connected to MySQL server")
    
    with connection.cursor() as cursor:
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS EM CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Database 'EM' created successfully (or already exists)")
        
        # Verify database exists
        cursor.execute("SHOW DATABASES LIKE 'EM'")
        result = cursor.fetchone()
        if result:
            print(f"✓ Database 'EM' verified")
    
    connection.close()
    print("\n✓ Database setup complete!")
    print("\nConnection string:")
    print("mysql+pymysql://root:Shash@123@localhost:3306/EM")
    print("\nNext: Update your .env file with this connection string")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nMake sure:")
    print("1. MySQL server is running")
    print("2. Username 'root' and password 'avi1234' are correct")
    print("3. You have CREATE DATABASE privileges")


