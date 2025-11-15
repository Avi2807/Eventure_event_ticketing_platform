# Event Management and Ticketing Platform

A comprehensive Flask-based REST API for managing events, venues, ticket sales, attendee management, and payment processing.

## Features

- **User Management**: Registration, authentication, and role-based access control (organizer, attendee, admin)
- **Venue Management**: Create and manage venues with capacity and amenities
- **Event Management**: Create, update, and manage events with full CRUD operations
- **Ticket Sales**: Multiple ticket types, pricing, and availability management
- **Seating Charts**: Support for seated, standing, and VIP sections with seat selection
- **Promotional Codes**: Percentage and fixed-amount discounts with usage limits
- **Order Processing**: Complete order lifecycle with payment integration
- **Payment Processing**: Support for multiple payment methods with refund capabilities
- **Check-in System**: QR code-based and manual check-in with tracking
- **Email Notifications**: Automated emails for order confirmations, tickets, reminders, refunds, and cancellations
- **Analytics**: Event sales summaries and attendance tracking

## Database Schema

The application uses MySQL with 15 tables:
- Users
- Venues
- Events
- Seating Sections
- Seats
- Ticket Types
- Promotional Codes
- Orders
- Tickets
- Payments
- Refunds
- Check-ins
- Email Notifications
- Event Analytics
- Venue Bookings

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd DBMS_Project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Create MySQL database**
   ```sql
   CREATE DATABASE event_management_db;
   ```

6. **Update DATABASE_URI in .env**
   ```
   DATABASE_URI=mysql+pymysql://username:password@localhost/event_management_db
   ```
   Replace `username`, `password`, and `localhost` with your MySQL credentials.

7. **Test database connection** (optional but recommended)
   ```bash
   python test_db_connection.py
   ```
   This will verify your database connectivity before running the app.

8. **Initialize database tables**
   ```bash
   python init_db.py
   ```
   This creates all the necessary database tables.

9. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication (`/api/auth`)
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update user profile

### Venues (`/api/venues`)
- `GET /api/venues` - Get all venues (with filters)
- `GET /api/venues/<id>` - Get venue by ID
- `POST /api/venues` - Create venue (admin/organizer)
- `POST /api/venues/<id>/bookings` - Create venue booking
- `GET /api/venues/<id>/bookings` - Get venue bookings

### Events (`/api/events`)
- `GET /api/events` - Get all events (with filters)
- `GET /api/events/<id>` - Get event by ID
- `POST /api/events` - Create event (organizer/admin)
- `PUT /api/events/<id>` - Update event
- `POST /api/events/<id>/ticket-types` - Create ticket type
- `GET /api/events/<id>/analytics` - Get event analytics

### Orders (`/api/orders`)
- `POST /api/orders` - Create new order
- `GET /api/orders` - Get user's orders
- `GET /api/orders/<id>` - Get order by ID
- `GET /api/orders/<id>/tickets` - Get order tickets

### Tickets (`/api/tickets`)
- `GET /api/tickets/<id>` - Get ticket by ID
- `GET /api/tickets/<id>/qr` - Get ticket QR code
- `GET /api/tickets/validate/<ticket_number>` - Validate ticket

### Promotional Codes (`/api/promo-codes`)
- `POST /api/promo-codes` - Create promo code (organizer/admin)
- `POST /api/promo-codes/validate` - Validate promo code
- `GET /api/promo-codes` - Get promo codes
- `GET /api/promo-codes/<id>` - Get promo code by ID
- `PUT /api/promo-codes/<id>` - Update promo code

### Seating (`/api/seating`)
- `POST /api/seating/venues/<id>/sections` - Create seating section
- `POST /api/seating/sections/<id>/seats` - Create seats
- `GET /api/seating/venues/<id>/chart` - Get seating chart
- `GET /api/seating/events/<id>/available-seats` - Get available seats for event

### Check-ins (`/api/check-ins`)
- `POST /api/check-ins` - Create check-in (staff/admin)
- `GET /api/check-ins/events/<id>` - Get event check-ins
- `GET /api/check-ins/tickets/<id>` - Get ticket check-in

### Payments (`/api/payments`)
- `GET /api/payments/orders/<id>` - Get order payments
- `GET /api/payments/<id>` - Get payment by ID
- `POST /api/payments/<id>/refund` - Process refund
- `GET /api/payments/refunds` - Get all refunds (admin)

## Usage Examples

### Register a User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "attendee"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Create an Event (requires authentication)
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "venue_id": 1,
    "event_name": "Concert 2024",
    "description": "Amazing concert",
    "category": "Music",
    "start_datetime": "2024-12-25T19:00:00",
    "end_datetime": "2024-12-25T22:00:00",
    "status": "published"
  }'
```

### Create an Order
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
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
    "promo_code": "SAVE10",
    "payment_method": "credit_card"
  }'
```

## Configuration

Key configuration options in `.env`:

- `DATABASE_URI`: MySQL connection string
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT token secret
- `MAIL_*`: Email configuration for notifications
- `TAX_RATE`: Default tax rate (default: 0.10 = 10%)
- `PAYMENT_GATEWAY`: Payment gateway to use

## Database Triggers

The application simulates database triggers in Python:
- After ticket insert: Updates ticket type availability
- After order with promo: Updates promotional code usage count
- After check-in: Updates ticket status to 'used'

## Email Notifications

The system sends automated emails for:
- Order confirmations
- Ticket issuance
- Event reminders
- Refund processing
- Event cancellations

Configure email settings in `.env` to enable email notifications.

## Payment Processing

Currently uses simulated payment processing. To integrate with real payment gateways:
1. Update `utils/payment_processor.py`
2. Add gateway-specific SDKs to `requirements.txt`
3. Configure gateway credentials in `.env`

## Security

- Password hashing using Werkzeug
- JWT-based authentication
- Role-based access control (RBAC)
- SQL injection protection via SQLAlchemy ORM

## Development

To run in development mode:
```bash
export FLASK_ENV=development
python app.py
```

## Production Deployment

1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure proper database connection pooling
4. Set up SSL/TLS certificates
5. Configure proper logging

## License

This project is created for educational purposes.

## Support

For issues or questions, please refer to the project documentation or contact the development team.

