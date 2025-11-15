# Frontend Documentation

## Overview
The Flask application includes a complete web frontend built with HTML, CSS, and JavaScript. The frontend provides a user-friendly interface for all platform features.

## File Structure

```
DBMS_Project/
├── templates/         # HTML templates (Jinja2)
│   ├── base.html      # Base template with navigation
│   ├── index.html     # Home page
│   ├── login.html     # Login page
│   ├── register.html  # Registration page
│   ├── dashboard.html # User dashboard
│   ├── events.html    # Events listing
│   ├── event_detail.html # Event details page
│   ├── create_event.html # Create event (organizers)
│   ├── order_detail.html # Order details
│   └── profile.html   # User profile
├── static/
│   ├── css/
│   │   └── style.css  # Main stylesheet
│   └── js/
│       └── main.js    # Main JavaScript utilities
└── routes/
    └── views.py       # Frontend route handlers
```

## Pages

### 1. Home Page (`/`)
- Hero section with call-to-action
- Featured events display
- Information for organizers and attendees

### 2. Login Page (`/login`)
- Email and password authentication
- Redirects to dashboard on success
- Stores JWT token in localStorage

### 3. Register Page (`/register`)
- User registration form
- Account type selection (attendee/organizer)
- Optional fields: phone, date of birth

### 4. Dashboard (`/dashboard`)
- **For Organizers:**
  - Event statistics
  - List of created events
  - Quick access to event management

- **For Attendees:**
  - Order statistics
  - Order history table
  - Quick access to browse events

### 5. Events Listing (`/events`)
- Grid view of all published events
- Filter by category and city
- Click to view event details

### 6. Event Details (`/events/<id>`)
- Full event information
- Available ticket types
- Purchase tickets functionality
- Venue information

### 7. Create Event (`/events/create`)
- Event creation form (organizers only)
- Venue selection
- Date/time picker
- Status selection (draft/published)

### 8. Order Details (`/orders/<id>`)
- Order summary
- Ticket list
- Payment information
- Order status

### 9. Profile (`/profile`)
- View and edit user profile
- Update personal information
- Account type display

## Styling

The application uses a modern, responsive design with:
- **Color Scheme:**
  - Primary: Indigo (#6366f1)
  - Secondary: Purple (#8b5cf6)
  - Success: Green (#10b981)
  - Danger: Red (#ef4444)

- **Features:**
  - Responsive grid layouts
  - Card-based design
  - Smooth transitions and hover effects
  - Mobile-friendly navigation

## JavaScript Functionality

### Authentication
- JWT token stored in localStorage
- Automatic token inclusion in API requests
- Redirect to login if token missing

### API Integration
- All pages fetch data from REST API endpoints
- Error handling with user-friendly messages
- Loading states with spinners

### Key Functions (main.js)
- `apiCall()` - Generic API request helper
- `formatCurrency()` - Currency formatting
- `formatDate()` - Date formatting
- `showLoading()` - Display loading spinner
- `showError()` - Display error messages
- `logout()` - Clear session and redirect

## Navigation

The navigation bar (in `base.html`) adapts based on:
- User authentication status
- User role (attendee/organizer/admin)
- Current page context

## Responsive Design

The frontend is fully responsive:
- Desktop: Full grid layouts, side-by-side forms
- Tablet: Adjusted grid columns
- Mobile: Single column, stacked navigation

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6 JavaScript features
- CSS Grid and Flexbox
- LocalStorage API

## Usage

1. **Start the Flask application:**
   ```bash
   python app.py
   ```

2. **Access the frontend:**
   - Open browser to `http://localhost:5000`
   - The home page will load automatically

3. **User Flow:**
   - Register/Login → Dashboard → Browse Events → Purchase Tickets → View Orders

## Customization

### Changing Colors
Edit CSS variables in `static/css/style.css`:
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    /* ... */
}
```

### Adding New Pages
1. Create HTML template in `templates/`
2. Add route in `routes/views.py`
3. Update navigation in `templates/base.html`

### Modifying API Endpoints
Update JavaScript fetch calls in template files to match your API structure.

## Notes

- The frontend uses client-side JavaScript for API calls
- JWT tokens are stored in localStorage (consider security implications)
- All forms include basic validation
- Error messages are displayed via alerts (can be enhanced with toast notifications)



