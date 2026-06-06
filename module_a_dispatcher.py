from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

deliveries = {}
couriers = [
    {"id": "courier_1", "name": "Иван", "available": True, "location": "Москва, ул. Тверская"},
    {"id": "courier_2", "name": "Петр", "available": True, "location": "Москва, ул. Арбат"},
    {"id": "courier_3", "name": "Сидор", "available": True, "location": "Москва, Кутузовский"}
]

@app.route('/assign', methods=['POST'])
def assign_delivery():
    data = request.get_json()
    
    order_id = data.get('order_id')
    address = data.get('address')
    recipient_phone = data.get('recipient_phone')
    
    if not order_id or not address:
        return jsonify({"error": "order_id and address required"}), 400
    
    available_courier = next((c for c in couriers if c['available']), None)
    
    if not available_courier:
        return jsonify({"error": "No available couriers"}), 503
    
    available_courier['available'] = False
    
    task_id = str(uuid.uuid4())[:8]
    
    delivery = {
        "task_id": task_id,
        "order_id": order_id,
        "address": address,
        "recipient_phone": recipient_phone,
        "courier_id": available_courier['id'],
        "courier_name": available_courier['name'],
        "status": "assigned"
    }
    
    deliveries[task_id] = delivery
    
    return jsonify({
        "task_id": task_id,
        "courier_id": available_courier['id'],
        "courier_name": available_courier['name'],
        "status": "assigned",
        "estimated_arrival": "30-45 minutes"
    }), 200

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    delivery = deliveries.get(task_id)
    if not delivery:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(delivery), 200

@app.route('/couriers', methods=['GET'])
def list_couriers():
    return jsonify(couriers), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
