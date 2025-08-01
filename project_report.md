# Vehicle Parking App - Project Report

## Student Details
- **Name**: [Your Name]
- **Roll Number**: [Your Roll Number]
- **Course**: Modern Application Development I
- **Semester**: [Current Semester]

## Project Details

### Problem Statement
Vehicle Parking App - V1 is a multi-user application that manages different parking lots, parking spots, and parked vehicles. The system supports two types of users: Administrators and Regular Users.

### Approach to Problem Statement
1. **Analysis**: Studied the requirements and identified the core entities (User, ParkingLot, ParkingSpot, Reservation)
2. **Design**: Created ER diagram and planned the database schema
3. **Implementation**: Used Flask framework with SQLAlchemy for database management
4. **Testing**: Implemented and tested all core functionalities
5. **Enhancement**: Added additional features like charts, API endpoints, and responsive UI

### Key Features Implemented
- **Admin Features**: Dashboard with statistics, parking lot management, spot monitoring, user management
- **User Features**: Registration, parking lot browsing, spot booking, cost calculation
- **Technical Features**: Responsive UI, form validation, API endpoints, real-time updates

## Frameworks and Libraries Used

### Backend
- **Flask 2.3.3**: Python web framework
- **Flask-SQLAlchemy 3.0.5**: Database ORM
- **Flask-Login 0.6.3**: User authentication
- **Werkzeug 2.3.7**: Security utilities

### Frontend
- **Bootstrap 5.1.3**: CSS framework for responsive design
- **Font Awesome 6.0.0**: Icon library
- **Chart.js**: JavaScript charting library
- **HTML5/CSS3**: Modern web standards

### Database
- **SQLite**: Lightweight database (programmatically created)

## ER Diagram

```
[User] 1 ---- * [Reservation] * ---- 1 [ParkingSpot]
                                    |
                                    |
[ParkingLot] 1 ---- * [ParkingSpot]
```

### Database Tables

1. **User Table**
   - id (Primary Key)
   - username (Unique)
   - email (Unique)
   - password_hash
   - is_admin (Boolean)
   - created_at

2. **ParkingLot Table**
   - id (Primary Key)
   - prime_location_name
   - price_per_hour
   - address
   - pin_code
   - maximum_number_of_spots
   - created_at

3. **ParkingSpot Table**
   - id (Primary Key)
   - lot_id (Foreign Key to ParkingLot)
   - spot_number
   - status (A-Available, O-Occupied)
   - created_at

4. **Reservation Table**
   - id (Primary Key)
   - spot_id (Foreign Key to ParkingSpot)
   - user_id (Foreign Key to User)
   - parking_timestamp
   - leaving_timestamp
   - parking_cost
   - status (active, completed, cancelled)
   - created_at

## API Resource Endpoints

### Public APIs
1. **GET /api/parking_lots**
   - Returns all parking lots with availability information
   - Response: JSON array of parking lot objects

2. **GET /api/spots/<lot_id>**
   - Returns all spots for a specific parking lot
   - Response: JSON array of spot objects

### Example API Response
```json
{
  "id": 1,
  "name": "Downtown Parking",
  "price_per_hour": 5.00,
  "address": "123 Main St",
  "total_spots": 50,
  "available_spots": 35
}
```

## Additional Features Implemented

### Core Requirements ✅
- [x] Admin and User login system
- [x] Admin dashboard with statistics and charts
- [x] Parking lot management (Create, Read, Update, Delete)
- [x] Automatic parking spot creation based on lot capacity
- [x] User registration and authentication
- [x] Parking spot booking and release
- [x] Cost calculation based on duration
- [x] Real-time spot status updates
- [x] User dashboard with parking history

### Additional Features ✅
- [x] Beautiful responsive UI with Bootstrap 5
- [x] Interactive charts using Chart.js
- [x] Form validation (frontend and backend)
- [x] REST API endpoints for external integration
- [x] Real-time statistics and analytics
- [x] Search and filter functionality
- [x] Progress bars for parking lot utilization
- [x] Auto-refresh for active reservations
- [x] Modular code structure with controllers and models

## Technical Implementation

### Project Structure
```
parking_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── models/               # Database models
│   └── database.py       # SQLAlchemy models
├── controllers/          # Application controllers
│   ├── auth_controller.py    # Authentication logic
│   ├── admin_controller.py   # Admin functionality
│   ├── user_controller.py    # User functionality
│   └── api_controller.py     # API endpoints
├── templates/            # HTML templates
├── static/               # Static files
│   ├── css/
│   └── images/
└── parking_app.db        # SQLite database
```

### Security Features
- Password hashing using Werkzeug
- Session management with Flask-Login
- Input validation and sanitization
- Access control for admin-only routes

## Demo Credentials

### Admin Account
- Username: `admin`
- Password: `admin123`

### Test User Account
- Register a new account through the registration form

## Installation Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py`
3. Access the application: `http://localhost:5000`

## Video Presentation Link

[Insert your Google Drive link to the presentation video here]

## AI/LLM Usage Declaration

[If you used any AI tools, please mention the extent of usage here]

---

**Note**: This project demonstrates proficiency in Flask web development, database design, user authentication, and modern web technologies. The modular architecture ensures maintainability and scalability of the application. 