from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

statuses = {}

statuses['demo_123'] = {
    "task_id": "demo_123",
    "status": "in_transit",
    "last_update": datetime.now().isoformat(),
    "location": {"lat": 55.7558, "lng": 37.6173}
}

@app.route('/track/update', methods=['POST'])
def update_location():
    data = request.get_json()
    task_id = data.get('task_id')
    lat = data.get('lat')
    lng = data.get('lng')
    
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    
    if task_id not in statuses:
        statuses[task_id] = {}
    
    statuses[task_id]['task_id'] = task_id
    statuses[task_id]['location'] = {"lat": lat, "lng": lng}
    statuses[task_id]['last_update'] = datetime.now().isoformat()
    
    return jsonify({"message": "Location updated"}), 200

@app.route('/track/<task_id>', methods=['GET'])
def get_tracking(task_id):
    data = statuses.get(task_id, {})
    if not data:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify({
        "task_id": task_id,
        "status": data.get('status', 'unknown'),
        "last_location": data.get('location'),
        "last_update": data.get('last_update')
    }), 200

@app.route('/track/complete', methods=['POST'])
def complete_delivery():
    data = request.get_json()
    task_id = data.get('task_id')
    proof = data.get('proof')
    
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    
    if task_id not in statuses:
        statuses[task_id] = {}
    
    statuses[task_id]['status'] = 'delivered'
    statuses[task_id]['proof'] = proof
    statuses[task_id]['completed_at'] = datetime.now().isoformat()
    
    return jsonify({"message": "Delivery completed", "status": "delivered"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
