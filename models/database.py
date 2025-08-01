import sqlite3
import os
from datetime import datetime
from flask import g

DATABASE = 'parking_app.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with tables and admin user."""
    # Only create database if it doesn't exist
    if not os.path.exists(DATABASE):
        db = sqlite3.connect(DATABASE)
        
        # Create tables
        db.executescript('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE parking_lots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prime_location_name TEXT NOT NULL,
                price_per_hour REAL NOT NULL,
                address TEXT NOT NULL,
                pin_code TEXT NOT NULL,
                maximum_number_of_spots INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE parking_spots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lot_id INTEGER NOT NULL,
                spot_number TEXT NOT NULL,
                status TEXT DEFAULT 'A',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lot_id) REFERENCES parking_lots (id)
            );
            
            CREATE TABLE reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spot_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                parking_timestamp TIMESTAMP NOT NULL,
                leaving_timestamp TIMESTAMP,
                parking_cost REAL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (spot_id) REFERENCES parking_spots (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        ''')
        
        # Create admin user
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin123')
        db.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@parking.com', admin_password, 'admin'))
        
        db.commit()
        db.close()
        print(f"Database '{DATABASE}' created successfully with tables and admin user.")
    else:
        print(f"Database '{DATABASE}' already exists. Skipping initialization.")

def ensure_tables_exist():
    """Ensure all required tables exist in the database."""
    db = get_db()
    
    # Check if tables exist
    tables = db.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('users', 'parking_lots', 'parking_spots', 'reservations')
    """).fetchall()
    
    existing_tables = [table['name'] for table in tables]
    required_tables = ['users', 'parking_lots', 'parking_spots', 'reservations']
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"Missing tables: {missing_tables}. Creating them...")
        
        if 'users' in missing_tables:
            db.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        if 'parking_lots' in missing_tables:
            db.execute('''
                CREATE TABLE parking_lots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prime_location_name TEXT NOT NULL,
                    price_per_hour REAL NOT NULL,
                    address TEXT NOT NULL,
                    pin_code TEXT NOT NULL,
                    maximum_number_of_spots INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        if 'parking_spots' in missing_tables:
            db.execute('''
                CREATE TABLE parking_spots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lot_id INTEGER NOT NULL,
                    spot_number TEXT NOT NULL,
                    status TEXT DEFAULT 'A',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lot_id) REFERENCES parking_lots (id)
                )
            ''')
        
        if 'reservations' in missing_tables:
            db.execute('''
                CREATE TABLE reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spot_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    parking_timestamp TIMESTAMP NOT NULL,
                    leaving_timestamp TIMESTAMP,
                    parking_cost REAL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (spot_id) REFERENCES parking_spots (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
        
        db.commit()
        print("Missing tables created successfully.")
    
    db.close()

def create_admin():
    """Create admin user if it doesn't exist."""
    try:
        # Try to use Flask's get_db (when in app context)
        db = get_db()
        admin = db.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin_password = generate_password_hash('admin123')
            db.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@parking.com', admin_password, 'admin'))
            db.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
    except RuntimeError:
        # If not in app context, create our own connection
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        admin = db.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin_password = generate_password_hash('admin123')
            db.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@parking.com', admin_password, 'admin'))
            db.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
        db.close() 