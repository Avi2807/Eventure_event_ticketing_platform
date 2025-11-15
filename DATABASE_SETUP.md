# Database Setup Guide

## Quick Setup

The Flask app is configured to connect to MySQL, but you need to:

1. **Create the database**
2. **Configure your connection string**
3. **Initialize the tables**

## Step-by-Step Instructions

### Option 1: Automated Setup (Recommended)

1. **Install MySQL connector** (if not already installed):
   ```bash
   pip install mysql-connector-python
   ```

2. **Run the setup script**:
   ```bash
   python setup_database.py
   ```
   
   This will:
   - Prompt for your MySQL credentials
   - Create the database if it doesn't exist
   - Show you the connection string to use

3. **Update your .env file** with the connection string shown

4. **Initialize tables**:
   ```bash
   python init_db.py
   ```

### Option 2: Manual Setup

1. **Create the database in MySQL**:
   ```sql
   CREATE DATABASE event_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Update .env file**:
   Open `.env` and update the `DATABASE_URI` line:
   ```
   DATABASE_URI=mysql+pymysql://username:password@localhost:3306/event_management_db
   ```
   
   Replace:
   - `username` with your MySQL username (usually `root`)
   - `password` with your MySQL password
   - `localhost` with your MySQL host (if different)
   - `3306` with your MySQL port (if different)
   - `event_management_db` with your database name (if different)

3. **Test the connection**:
   ```bash
   python test_db_connection.py
   ```

4. **Initialize tables**:
   ```bash
   python init_db.py
   ```

## Default Configuration

The app comes with a default connection string:
```
mysql+pymysql://root:password@localhost/event_management_db
```

**You MUST update this** with your actual MySQL credentials in the `.env` file.

## Connection String Format

```
mysql+pymysql://username:password@host:port/database_name
```

Examples:
- Local MySQL with default port: `mysql+pymysql://root:mypassword@localhost:3306/event_management_db`
- Remote MySQL: `mysql+pymysql://user:pass@192.168.1.100:3306/event_management_db`
- Without port (defaults to 3306): `mysql+pymysql://root:password@localhost/event_management_db`

## Troubleshooting

### "Access denied" error
- Check your MySQL username and password
- Ensure the user has CREATE DATABASE privileges

### "Can't connect to MySQL server"
- Make sure MySQL service is running
- Check if MySQL is listening on the correct host/port
- Verify firewall settings

### "Unknown database"
- Create the database first (see manual setup above)
- Check the database name in your connection string

### "cryptography package required"
- Install: `pip install cryptography`
- This is needed for secure password authentication in MySQL 8.0+

## Verify Connection

After setup, test your connection:
```bash
python test_db_connection.py
```

This will verify:
- MySQL connection
- Database existence
- Table creation readiness

## Next Steps

Once the database is set up:
1. Run `python init_db.py` to create all tables
2. Run `python app.py` to start the Flask application
3. Access the app at `http://localhost:5000`


