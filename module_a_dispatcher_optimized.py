from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db, get_db, Courier, Delivery
from cache import cache
from performance import perf_monitor

app = Flask(__name__)
CORS(app)
init_db()

@cache.cached(ttl_seconds=60, key_prefix="couriers_list")
def get_cached_couriers():
    """Get couriers with caching"""
    db = next(get_db())
    couriers = db.query(Courier).all()
    result = [{
        "id": c.courier_id,
        "name": c.name,
        "available": c.available,
        "location": c.location
    } for c in couriers]
    db.close()
    return result

@perf_monitor.measure_time(name="assign_delivery")
@app.route('/assign', methods=['POST'])
def assign_delivery():
    data = request.get_json()
    order_id = data.get('order_id')
    address = data.get('address')
    recipient_phone = data.get('recipient_phone')
    
    if not order_id or not address:
        return jsonify({"error": "order_id and address required"}), 400
    
    db = next(get_db())
    courier = db.query(Courier).filter(Courier.available == True).first()
    
    if not courier:
        db.close()
        return jsonify({"error": "No available couriers"}), 503
    
    courier_id = courier.courier_id
    courier_name = courier.name
    
    courier.available = False
    task_id = str(uuid.uuid4())[:8]
    
    delivery = Delivery(
        task_id=task_id,
        order_id=order_id,
        address=address,
        recipient_phone=recipient_phone,
        courier_id=courier_id,
        courier_name=courier_name,
        status="assigned",
        created_at=datetime.now(timezone.utc)
    )
    db.add(delivery)
    db.commit()
    db.close()
    
    # Invalidate cache when data changes
    cache.delete("couriers_list")
    
    return jsonify({
        "task_id": task_id,
        "courier_id": courier_id,
        "courier_name": courier_name,
        "status": "assigned"
    }), 200

@perf_monitor.measure_time(name="get_couriers")
@app.route('/couriers', methods=['GET'])
def list_couriers():
    result = get_cached_couriers()
    return jsonify(result), 200

@perf_monitor.measure_time(name="get_deliveries")
@app.route('/deliveries', methods=['GET'])
def list_deliveries():
    db = next(get_db())
    deliveries = db.query(Delivery).all()
    result = [{
        "task_id": d.task_id,
        "order_id": d.order_id,
        "status": d.status,
        "courier_name": d.courier_name
    } for d in deliveries]
    db.close()
    return jsonify(result), 200

@app.route('/performance/stats', methods=['GET'])
def get_performance_stats():
    return jsonify(perf_monitor.get_statistics()), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
