from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.database import get_db
from datetime import datetime

def admin_dashboard():
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    parking_lots_raw = db.execute('SELECT * FROM parking_lots').fetchall()
    parking_lots = [dict(lot) for lot in parking_lots_raw]
    total_spots = sum(lot['maximum_number_of_spots'] for lot in parking_lots)
    occupied_spots = db.execute("SELECT COUNT(*) FROM parking_spots WHERE status = 'O'").fetchone()[0]
    available_spots = total_spots - occupied_spots
    total_users = db.execute("SELECT COUNT(*) FROM users WHERE role = 'user'").fetchone()[0]
    return render_template('admin_dashboard.html', 
                         parking_lots=parking_lots,
                         total_spots=total_spots,
                         occupied_spots=occupied_spots,
                         available_spots=available_spots,
                         total_users=total_users)

def admin_parking_lots():
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    if request.method == 'POST':
        prime_location_name = request.form['prime_location_name']
        price_per_hour = float(request.form['price_per_hour'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        maximum_number_of_spots = int(request.form['maximum_number_of_spots'])
        db.execute('''
            INSERT INTO parking_lots (prime_location_name, price_per_hour, address, pin_code, maximum_number_of_spots)
            VALUES (?, ?, ?, ?, ?)
        ''', (prime_location_name, price_per_hour, address, pin_code, maximum_number_of_spots))
        db.commit()
        lot_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        for i in range(1, maximum_number_of_spots + 1):
            spot_number = f"{prime_location_name}-{i:03d}"
            db.execute('''
                INSERT INTO parking_spots (lot_id, spot_number, status)
                VALUES (?, ?, 'A')
            ''', (lot_id, spot_number))
        db.commit()
        flash('Parking lot created successfully!', 'success')
        return redirect(url_for('admin_parking_lots_route'))
    
    parking_lots_raw = db.execute('SELECT * FROM parking_lots').fetchall()
    parking_lots = []
    for lot_row in parking_lots_raw:
        lot = dict(lot_row)
        occupied = db.execute('SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = "O"', (lot['id'],)).fetchone()[0]
        lot['available_spots'] = lot['maximum_number_of_spots'] - occupied
        parking_lots.append(lot)
    return render_template('admin_parking_lots.html', parking_lots=parking_lots)

def edit_parking_lot(lot_id):
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    parking_lot = db.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
    if not parking_lot:
        flash('Parking lot not found!', 'error')
        return redirect(url_for('admin_parking_lots_route'))
    if request.method == 'POST':
        occupied_spots = db.execute('SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = "O"', (lot_id,)).fetchone()[0]
        if occupied_spots > 0:
            flash('Cannot edit parking lot with occupied spots!', 'error')
            return redirect(url_for('admin_parking_lots_route'))
        prime_location_name = request.form['prime_location_name']
        price_per_hour = float(request.form['price_per_hour'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        new_max_spots = int(request.form['maximum_number_of_spots'])
        db.execute('''
            UPDATE parking_lots SET prime_location_name=?, price_per_hour=?, address=?, pin_code=?, maximum_number_of_spots=? WHERE id=?
        ''', (prime_location_name, price_per_hour, address, pin_code, new_max_spots, lot_id))
        db.execute('DELETE FROM parking_spots WHERE lot_id = ?', (lot_id,))
        for i in range(1, new_max_spots + 1):
            spot_number = f"{prime_location_name}-{i:03d}"
            db.execute('''
                INSERT INTO parking_spots (lot_id, spot_number, status)
                VALUES (?, ?, 'A')
            ''', (lot_id, spot_number))
        db.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin_parking_lots_route'))
    return render_template('edit_parking_lot.html', parking_lot=parking_lot)

def delete_parking_lot(lot_id):
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    occupied_spots = db.execute('SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = "O"', (lot_id,)).fetchone()[0]
    if occupied_spots > 0:
        flash('Cannot delete parking lot with occupied spots!', 'error')
        return redirect(url_for('admin_parking_lots_route'))
    db.execute('DELETE FROM parking_spots WHERE lot_id = ?', (lot_id,))
    db.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
    db.commit()
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin_parking_lots_route'))

def admin_spots():
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    parking_spots = db.execute('''
        SELECT parking_spots.*, parking_lots.prime_location_name FROM parking_spots
        JOIN parking_lots ON parking_spots.lot_id = parking_lots.id
    ''').fetchall()
    # Attach current reservation if occupied
    spots = []
    for spot in parking_spots:
        spot = dict(spot)
        if spot['status'] == 'O':
            reservation = db.execute('''
                SELECT r.*, u.username FROM reservations r
                JOIN users u ON r.user_id = u.id
                WHERE r.spot_id = ? AND r.status = 'active' ORDER BY r.parking_timestamp DESC LIMIT 1
            ''', (spot['id'],)).fetchone()
            spot['current_reservation'] = reservation
        else:
            spot['current_reservation'] = None
        spots.append(spot)
    return render_template('admin_spots.html', parking_spots=spots)

def admin_users():
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    users_raw = db.execute('SELECT * FROM users').fetchall()
    users = []
    for user_row in users_raw:
        user = dict(user_row)
        reservations = db.execute('SELECT * FROM reservations WHERE user_id = ?', (user['id'],)).fetchall()
        user['reservations'] = reservations
        users.append(user)
    return render_template('admin_users.html', users=users)

def admin_release_spot(reservation_id):
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    reservation = db.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
    if not reservation:
        flash('Reservation not found!', 'error')
        return redirect(url_for('admin_spots_route'))
    db.execute('UPDATE reservations SET status = "completed", leaving_timestamp = ? WHERE id = ?', (datetime.now(), reservation_id))
    db.execute('UPDATE parking_spots SET status = "A" WHERE id = ?', (reservation['spot_id'],))
    db.commit()
    flash('Spot released successfully!', 'success')
    return redirect(url_for('admin_spots_route'))

def admin_delete_user(user_id):
    if getattr(current_user, 'role', None) != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_users_route')) 