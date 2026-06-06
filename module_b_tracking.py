from flask import Flask, request, jsonify
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db, get_db, Delivery, TrackingHistory

app = Flask(__name__)
init_db()

@app.route('/track/update', methods=['POST'])
def update_location():
    data = request.get_json()
    task_id = data.get('task_id')
    lat = data.get('lat')
    lng = data.get('lng')
    
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    
    db = next(get_db())
    history = TrackingHistory(
        task_id=task_id,
        lat=lat,
        lng=lng,
        status="in_transit"
    )
    db.add(history)
    
    delivery = db.query(Delivery).filter(Delivery.task_id == task_id).first()
    if delivery:
        delivery.status = "in_transit"
    
    db.commit()
    db.close()
    
    return jsonify({"message": "Location updated"}), 200

@app.route('/track/<task_id>', methods=['GET'])
def get_tracking(task_id):
    db = next(get_db())
    delivery = db.query(Delivery).filter(Delivery.task_id == task_id).first()
    history = db.query(TrackingHistory).filter(TrackingHistory.task_id == task_id).order_by(TrackingHistory.updated_at.desc()).first()
    db.close()
    
    return jsonify({
        "task_id": task_id,
        "status": delivery.status if delivery else "unknown",
        "last_location": {"lat": history.lat, "lng": history.lng} if history else None,
        "last_update": history.updated_at.isoformat() if history else None
    }), 200

@app.route('/track/complete', methods=['POST'])
def complete_delivery():
    data = request.get_json()
    task_id = data.get('task_id')
    proof = data.get('proof')
    
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    
    db = next(get_db())
    delivery = db.query(Delivery).filter(Delivery.task_id == task_id).first()
    if delivery:
        delivery.status = "delivered"
        delivery.proof = proof
        delivery.completed_at = datetime.utcnow()
        db.commit()
    
    db.close()
    return jsonify({"message": "Delivery completed", "status": "delivered"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
