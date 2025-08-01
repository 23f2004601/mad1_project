from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.database import get_db
from datetime import datetime

def user_dashboard():
    if getattr(current_user, 'role', None) == 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    active_reservations_raw = db.execute('''
        SELECT r.*, s.spot_number, l.prime_location_name, l.price_per_hour, s.lot_id
        FROM reservations r
        JOIN parking_spots s ON r.spot_id = s.id
        JOIN parking_lots l ON s.lot_id = l.id
        WHERE r.user_id = ? AND r.status = 'active'
    ''', (current_user.id,)).fetchall()
    
    completed_reservations_raw = db.execute('''
        SELECT r.*, s.spot_number, l.prime_location_name, l.price_per_hour, s.lot_id
        FROM reservations r
        JOIN parking_spots s ON r.spot_id = s.id
        JOIN parking_lots l ON s.lot_id = l.id
        WHERE r.user_id = ? AND r.status = 'completed'
        ORDER BY r.leaving_timestamp DESC LIMIT 5
    ''', (current_user.id,)).fetchall()
    
    # Convert to dictionaries and calculate durations
    active_reservations = []
    for r in active_reservations_raw:
        reservation = dict(r)
        if reservation['parking_timestamp']:
            parking_time = datetime.fromisoformat(reservation['parking_timestamp']) if isinstance(reservation['parking_timestamp'], str) else reservation['parking_timestamp']
            duration = (datetime.now() - parking_time).total_seconds() / 3600
            reservation['current_duration'] = duration
            reservation['estimated_cost'] = duration * reservation['price_per_hour']
        active_reservations.append(reservation)
    
    completed_reservations = []
    for r in completed_reservations_raw:
        reservation = dict(r)
        if reservation['parking_timestamp'] and reservation['leaving_timestamp']:
            parking_time = datetime.fromisoformat(reservation['parking_timestamp']) if isinstance(reservation['parking_timestamp'], str) else reservation['parking_timestamp']
            leaving_time = datetime.fromisoformat(reservation['leaving_timestamp']) if isinstance(reservation['leaving_timestamp'], str) else reservation['leaving_timestamp']
            duration = (leaving_time - parking_time).total_seconds() / 3600
            reservation['duration'] = duration
        completed_reservations.append(reservation)
    
    total_parking_time = sum(
        ((r['leaving_timestamp'] and r['parking_timestamp']) and (datetime.fromisoformat(r['leaving_timestamp']) - datetime.fromisoformat(r['parking_timestamp'])).total_seconds() / 3600) or 0
        for r in completed_reservations_raw
    )
    total_cost = sum(r['parking_cost'] or 0 for r in completed_reservations_raw)
    
    return render_template('user_dashboard.html',
                         active_reservations=active_reservations,
                         completed_reservations=completed_reservations,
                         total_parking_time=total_parking_time,
                         total_cost=total_cost)

def user_parking_lots():
    if getattr(current_user, 'role', None) == 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    parking_lots = db.execute('SELECT * FROM parking_lots').fetchall()
    lots = []
    for lot in parking_lots:
        occupied_spots = db.execute('SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = "O"', (lot['id'],)).fetchone()[0]
        available_spots = lot['maximum_number_of_spots'] - occupied_spots
        lot = dict(lot)
        lot['available_spots'] = available_spots
        lots.append(lot)
    return render_template('user_parking_lots.html', parking_lots=lots)

def book_spot(lot_id):
    if getattr(current_user, 'role', None) == 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    active_reservation = db.execute('SELECT * FROM reservations WHERE user_id = ? AND status = "active"', (current_user.id,)).fetchone()
    if active_reservation:
        flash('You already have an active parking reservation!', 'error')
        return redirect(url_for('user_parking_lots_route'))
    available_spot = db.execute('SELECT * FROM parking_spots WHERE lot_id = ? AND status = "A" LIMIT 1', (lot_id,)).fetchone()
    if not available_spot:
        flash('No available spots in this parking lot!', 'error')
        return redirect(url_for('user_parking_lots_route'))
    db.execute('''
        INSERT INTO reservations (spot_id, user_id, parking_timestamp, status)
        VALUES (?, ?, ?, 'active')
    ''', (available_spot['id'], current_user.id, datetime.now()))
    db.execute('UPDATE parking_spots SET status = "O" WHERE id = ?', (available_spot['id'],))
    db.commit()
    flash('Parking spot booked successfully!', 'success')
    return redirect(url_for('user_dashboard_route'))

def release_spot(reservation_id):
    if getattr(current_user, 'role', None) == 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    reservation = db.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
    if not reservation or reservation['user_id'] != current_user.id:
        flash('Access denied!', 'error')
        return redirect(url_for('user_dashboard_route'))
    if reservation['status'] != 'active':
        flash('Reservation is not active!', 'error')
        return redirect(url_for('user_dashboard_route'))
    leaving_time = datetime.now()
    parking_timestamp = datetime.fromisoformat(reservation['parking_timestamp']) if isinstance(reservation['parking_timestamp'], str) else reservation['parking_timestamp']
    parking_duration = (leaving_time - parking_timestamp).total_seconds() / 3600
    lot = db.execute('''
        SELECT l.price_per_hour FROM parking_lots l
        JOIN parking_spots s ON l.id = s.lot_id
        WHERE s.id = ?
    ''', (reservation['spot_id'],)).fetchone()
    price_per_hour = lot['price_per_hour'] if lot else 0
    parking_cost = parking_duration * price_per_hour
    db.execute('''
        UPDATE reservations SET leaving_timestamp = ?, parking_cost = ?, status = 'completed' WHERE id = ?
    ''', (leaving_time, parking_cost, reservation_id))
    db.execute('UPDATE parking_spots SET status = "A" WHERE id = ?', (reservation['spot_id'],))
    db.commit()
    flash(f'Spot released! Parking cost: ${parking_cost:.2f}', 'success')
    return redirect(url_for('user_dashboard_route')) 