from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db

class User(UserMixin):
    def __init__(self, row):
        self.id = row['id']
        self.username = row['username']
        self.email = row['email']
        self.password_hash = row['password_hash']
        self.role = row['role']
        self.created_at = row['created_at']
    def get_id(self):
        return str(self.id)
    @property
    def is_active(self):
        return True
    @property
    def is_authenticated(self):
        return True
    @property
    def is_anonymous(self):
        return False

def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        db = get_db()
        
        # Check if username exists
        existing_user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        # Check if email exists
        existing_email = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_email:
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        # Create new user
        db.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', (username, email, generate_password_hash(password), 'user'))
        db.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login_route'))
    
    return render_template('register.html')

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"Login attempt for username: {username}")
        
        db = get_db()
        user_row = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user_row:
            print(f"User found: {user_row['username']}, role: {user_row['role']}")
            print(f"Stored password hash: {user_row['password_hash'][:20]}...")
            password_check = check_password_hash(user_row['password_hash'], password)
            print(f"Password check result: {password_check}")
            
            if password_check:
                print("Password check passed")
                user = User(user_row)
                login_user(user)
                print(f"User logged in, redirecting to {'admin' if user.role == 'admin' else 'user'} dashboard")
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard_route'))
                else:
                    return redirect(url_for('user_dashboard_route'))
            else:
                print("Password check failed")
                flash('Invalid username or password!', 'error')
        else:
            print("User not found")
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def create_admin():
    db = get_db()
    admin = db.execute('SELECT * FROM users WHERE role = ?', ('admin',)).fetchone()
    if not admin:
        db.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@parking.com', generate_password_hash('admin123'), 'admin'))
        db.commit() 