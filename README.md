# Vehicle Parking App

A comprehensive parking management system built with Flask, SQLite, and Bootstrap. This application allows administrators to manage parking lots and users to book parking spots.

## Features

### Admin Features
- **Dashboard**: View statistics and charts for parking utilization
- **Parking Lot Management**: Create, edit, and delete parking lots
- **Spot Management**: Monitor all parking spots and their status
- **User Management**: View registered users and their activities
- **Real-time Analytics**: Charts showing parking utilization and revenue

### User Features
- **Registration & Login**: Secure user authentication
- **Parking Lot Browsing**: View available parking lots with real-time availability
- **Spot Booking**: Automatically book available parking spots
- **Spot Release**: Release parking spots and calculate costs
- **Parking History**: View past parking sessions and costs
- **Dashboard**: Personal statistics and active reservations

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (programmatically created)
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login
- **Charts**: Chart.js
- **Icons**: Font Awesome

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download the project files**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`

## Default Admin Account

The application automatically creates an admin account when first run:

- **Username**: `admin`
- **Password**: `admin123`

## Database Schema

### Tables

1. **User**
   - id (Primary Key)
   - username (Unique)
   - email (Unique)
   - password_hash
   - is_admin (Boolean)
   - created_at

2. **ParkingLot**
   - id (Primary Key)
   - prime_location_name
   - price_per_hour
   - address
   - pin_code
   - maximum_number_of_spots
   - created_at

3. **ParkingSpot**
   - id (Primary Key)
   - lot_id (Foreign Key to ParkingLot)
   - spot_number
   - status (A-Available, O-Occupied)
   - created_at

4. **Reservation**
   - id (Primary Key)
   - spot_id (Foreign Key to ParkingSpot)
   - user_id (Foreign Key to User)
   - parking_timestamp
   - leaving_timestamp
   - parking_cost
   - status (active, completed, cancelled)
   - created_at

## API Endpoints

### Public APIs
- `GET /api/parking_lots` - Get all parking lots with availability
- `GET /api/spots/<lot_id>` - Get spots for a specific parking lot

## Usage Guide

### For Administrators

1. **Login** with admin credentials
2. **Create Parking Lots**:
   - Go to "Parking Lots" section
   - Fill in location details, pricing, and number of spots
   - Spots are automatically created based on the maximum number
3. **Monitor Spots**:
   - View all parking spots and their current status
   - Filter by parking lot
   - See current reservations and user details
4. **Manage Users**:
   - View all registered users
   - Monitor user activities and revenue

### For Users

1. **Register** a new account or **Login** with existing credentials
2. **Browse Parking Lots**:
   - View available parking lots
   - See real-time availability and pricing
3. **Book a Spot**:
   - Click "Book Spot" on any available parking lot
   - Spots are automatically assigned
4. **Release Spot**:
   - Go to dashboard and click "Release Spot"
   - Cost is automatically calculated based on duration

## Features Implemented

### Core Requirements ✅
- [x] Admin and User login system
- [x] Admin dashboard with statistics
- [x] Parking lot management (CRUD operations)
- [x] Automatic parking spot creation
- [x] User registration and authentication
- [x] Parking spot booking and release
- [x] Cost calculation based on duration
- [x] Real-time spot status updates
- [x] User dashboard with history

### Additional Features ✅
- [x] Beautiful responsive UI with Bootstrap
- [x] Interactive charts using Chart.js
- [x] Form validation (frontend and backend)
- [x] API endpoints for external integration
- [x] Real-time statistics and analytics
- [x] Search and filter functionality
- [x] Progress bars for parking lot utilization
- [x] Auto-refresh for active reservations

## Security Features

- Password hashing using Werkzeug
- Session management with Flask-Login
- Input validation and sanitization
- CSRF protection through Flask forms
- Access control for admin-only routes

## Project Structure

```
parking_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── models/               # Database models
│   └── database.py       # SQLAlchemy models
├── controllers/          # Application controllers
│   ├── auth_controller.py    # Authentication logic
│   ├── admin_controller.py   # Admin functionality
│   ├── user_controller.py    # User functionality
│   └── api_controller.py     # API endpoints
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Landing page
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── admin_dashboard.html
│   ├── admin_parking_lots.html
│   ├── admin_spots.html
│   ├── admin_users.html
│   ├── edit_parking_lot.html
│   ├── user_dashboard.html
│   └── user_parking_lots.html
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom CSS styles
│   └── images/           # Image assets
└── parking_app.db        # SQLite database (created automatically)
```

## Demo Credentials

### Admin Account
- Username: `admin`
- Password: `admin123`

### Test User Account
- Register a new account through the registration form

## Troubleshooting

1. **Database Issues**: Delete `parking_app.db` and restart the application
2. **Port Already in Use**: Change the port in `app.py` or kill the existing process
3. **Dependencies**: Ensure all requirements are installed with `pip install -r requirements.txt`

## Future Enhancements

- Payment gateway integration
- Mobile app development
- Advanced analytics and reporting
- Email notifications
- QR code generation for spots
- Multi-language support
- Advanced search and filtering

## License

This project is created for educational purposes as part of the Modern Application Development course. 