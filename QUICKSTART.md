# Quick Start Guide

## Prerequisites
- Python 3.8+
- MySQL 5.7+ or MySQL 8.0+
- pip (Python package manager)

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
Create a MySQL database:
```sql
CREATE DATABASE event_management_db;
```

### 3. Configure Environment
Copy `.env.example` to `.env` and update with your settings:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and set:
- `DATABASE_URI` with your MySQL credentials
- `SECRET_KEY` and `JWT_SECRET_KEY` (generate random strings)
- Email settings if you want email notifications

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run the Application
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Testing the API

### 1. Register a User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "organizer@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "organizer"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "organizer@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### 3. Create a Venue
```bash
curl -X POST http://localhost:5000/api/venues \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "venue_name": "Concert Hall",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "capacity": 1000,
    "description": "A beautiful concert hall"
  }'
```

### 4. Create an Event
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "venue_id": 1,
    "event_name": "Summer Concert 2024",
    "description": "Amazing summer concert",
    "category": "Music",
    "start_datetime": "2024-12-25T19:00:00",
    "end_datetime": "2024-12-25T22:00:00",
    "status": "published"
  }'
```

### 4. Create Ticket Types
```bash
curl -X POST http://localhost:5000/api/events/1/ticket-types \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "type_name": "General Admission",
    "price": 50.00,
    "quantity_total": 100,
    "sale_start": "2024-01-01T00:00:00",
    "sale_end": "2024-12-24T23:59:59",
    "min_purchase": 1,
    "max_purchase": 10
  }'
```

### 5. Create an Order (as attendee)
Register an attendee user, login, then:
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ATTENDEE_ACCESS_TOKEN" \
  -d '{
    "event_id": 1,
    "ticket_items": [
      {
        "ticket_type_id": 1,
        "quantity": 2,
        "attendees": [
          {"name": "John Doe", "email": "john@example.com"},
          {"name": "Jane Doe", "email": "jane@example.com"}
        ]
      }
    ],
    "payment_method": "credit_card"
  }'
```

## API Documentation

See `README.md` for complete API documentation.

## Common Issues

### Database Connection Error
- Verify MySQL is running
- Check `DATABASE_URI` in `.env`
- Ensure database exists

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're in the project directory

### Email Not Working
- Configure email settings in `.env`
- For Gmail, use an App Password, not your regular password

