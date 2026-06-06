from flask import Flask, request, jsonify
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db, get_db, Courier, Delivery

app = Flask(__name__)
init_db()

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
    
    # Save values BEFORE closing session
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
        status="assigned"
    )
    db.add(delivery)
    db.commit()
    db.close()
    
    return jsonify({
        "task_id": task_id,
        "courier_id": courier_id,
        "courier_name": courier_name,
        "status": "assigned"
    }), 200

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    db = next(get_db())
    delivery = db.query(Delivery).filter(Delivery.task_id == task_id).first()
    if not delivery:
        db.close()
        return jsonify({"error": "Task not found"}), 404
    
    result = {
        "task_id": delivery.task_id,
        "order_id": delivery.order_id,
        "status": delivery.status,
        "courier_name": delivery.courier_name
    }
    db.close()
    return jsonify(result), 200

@app.route('/couriers', methods=['GET'])
def list_couriers():
    db = next(get_db())
    couriers = db.query(Courier).all()
    result = [{
        "id": c.courier_id,
        "name": c.name,
        "available": c.available,
        "location": c.location
    } for c in couriers]
    db.close()
    return jsonify(result), 200

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
