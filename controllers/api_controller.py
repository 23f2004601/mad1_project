from flask import jsonify, request
from models.database import get_db

def api_parking_lots():
    db = get_db()
    lots = db.execute('SELECT * FROM parking_lots').fetchall()
    result = []
    for lot in lots:
        occupied = db.execute('SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = "O"', (lot['id'],)).fetchone()[0]
        available_spots = lot['maximum_number_of_spots'] - occupied
        result.append({
            'id': lot['id'],
            'name': lot['prime_location_name'],
            'price_per_hour': lot['price_per_hour'],
            'address': lot['address'],
            'total_spots': lot['maximum_number_of_spots'],
            'available_spots': available_spots
        })
    return jsonify(result)

def api_spots():
    db = get_db()
    lot_id = request.args.get('lot_id', type=int)
    if lot_id:
        spots = db.execute('SELECT * FROM parking_spots WHERE lot_id = ?', (lot_id,)).fetchall()
    else:
        spots = db.execute('SELECT * FROM parking_spots').fetchall()
    return jsonify([{
        'id': spot['id'],
        'spot_number': spot['spot_number'],
        'status': spot['status'],
        'is_occupied': spot['status'] == 'O'
    } for spot in spots])

def api_reservations():
    db = get_db()
    reservations = db.execute('SELECT * FROM reservations').fetchall()
    return jsonify([dict(res) for res in reservations]) 