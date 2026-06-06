from flask import Flask, request, jsonify
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/delivery_db?driver=ODBC+Driver+18+for+SQL+Server&trustservercertificate=yes')
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

# In-memory fallback
deliveries = {}
couriers = [
    {"id": "courier_1", "name": "Ivan", "available": True, "location": "Moscow, Tverskaya"},
    {"id": "courier_2", "name": "Petr", "available": True, "location": "Moscow, Arbat"},
    {"id": "courier_3", "name": "Sidor", "available": True, "location": "Moscow, Kutuzovsky"}
]

def get_courier_from_db():
    try:
        from database.models import Courier
        session = Session()
        courier = session.query(Courier).filter(Courier.available == True).first()
        if courier:
            courier.available = False
            session.commit()
            result = {"id": courier.courier_id, "name": courier.name, "location": courier.location}
            session.close()
            return result
        session.close()
        return None
    except Exception as e:
        print(f"DB error: {e}")
        return None

@app.route('/assign', methods=['POST'])
def assign_delivery():
    data = request.get_json()
    
    order_id = data.get('order_id')
    address = data.get('address')
    recipient_phone = data.get('recipient_phone')
    
    if not order_id or not address:
        return jsonify({"error": "order_id and address required"}), 400
    
    # Try DB first, fallback to memory
    available_courier = get_courier_from_db()
    
    if not available_courier:
        available_courier = next((c for c in couriers if c['available']), None)
        if available_courier:
            available_courier['available'] = False
    
    if not available_courier:
        return jsonify({"error": "No available couriers"}), 503
    
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
