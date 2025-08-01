from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import os

# Import models and controllers
from models.database import init_db, get_db, close_db, create_admin, ensure_tables_exist
from controllers.auth_controller import register, login, logout, User
from controllers.admin_controller import (
    admin_dashboard, admin_parking_lots, edit_parking_lot, 
    delete_parking_lot, admin_spots, admin_users, admin_release_spot, admin_delete_user
)
from controllers.user_controller import (
    user_dashboard, user_parking_lots, book_spot, release_spot
)
from controllers.api_controller import api_parking_lots, api_spots, api_reservations

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Register close_db function
app.teardown_appcontext(close_db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_route'

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user_row = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user_row:
        return User(user_row)
    return None

# Context processor for current time
@app.context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc)}

def no_cache(response):
    """Add headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', None) == 'admin':
            return redirect(url_for('admin_dashboard_route'))
        else:
            return redirect(url_for('user_dashboard_route'))
    response = make_response(render_template('index.html'))
    return no_cache(response)

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', None) == 'admin':
            return redirect(url_for('admin_dashboard_route'))
        else:
            return redirect(url_for('user_dashboard_route'))
    response = make_response(register())
    return no_cache(response)

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', None) == 'admin':
            return redirect(url_for('admin_dashboard_route'))
        else:
            return redirect(url_for('user_dashboard_route'))
    response = make_response(login())
    return no_cache(response)

@app.route('/logout')
@login_required
def logout_route():
    return logout()

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard_route():
    return admin_dashboard()

@app.route('/admin/parking-lots', methods=['GET', 'POST'])
@login_required
def admin_parking_lots_route():
    return admin_parking_lots()

@app.route('/admin/parking-lots/<int:lot_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_parking_lot_route(lot_id):
    return edit_parking_lot(lot_id)

@app.route('/admin/parking-lots/<int:lot_id>/delete')
@login_required
def delete_parking_lot_route(lot_id):
    return delete_parking_lot(lot_id)

@app.route('/admin/spots')
@login_required
def admin_spots_route():
    return admin_spots()

@app.route('/admin/spots/<int:reservation_id>/release')
@login_required
def admin_release_spot_route(reservation_id):
    return admin_release_spot(reservation_id)

@app.route('/admin/users')
@login_required
def admin_users_route():
    return admin_users()

@app.route('/admin/users/<int:user_id>/delete')
@login_required
def admin_delete_user_route(user_id):
    return admin_delete_user(user_id)

# User routes
@app.route('/user/dashboard')
@login_required
def user_dashboard_route():
    return user_dashboard()

@app.route('/user/parking-lots')
@login_required
def user_parking_lots_route():
    return user_parking_lots()

@app.route('/user/parking-lots/<int:lot_id>/book')
@login_required
def book_spot_route(lot_id):
    return book_spot(lot_id)

@app.route('/user/reservations/<int:reservation_id>/release')
@login_required
def release_spot_route(reservation_id):
    return release_spot(reservation_id)

# API routes
@app.route('/api/parking-lots')
def api_parking_lots_route():
    return api_parking_lots()

@app.route('/api/spots')
def api_spots_route():
    return api_spots()

@app.route('/api/reservations')
def api_reservations_route():
    return api_reservations()

if __name__ == '__main__':
    # Initialize database (creates if doesn't exist)
    init_db()
    
    # Create admin user (works both in and out of app context)
    create_admin()
    
    # Ensure tables exist within app context
    with app.app_context():
        ensure_tables_exist()
    
    app.run(debug=True) 