from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db, get_db, Notification

app = Flask(__name__)
CORS(app)  # Enable CORS
init_db()

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.get_json()
    recipient = data.get('recipient')
    message_type = data.get('type', 'sms')
    message = data.get('message')
    order_id = data.get('order_id')
    
    if not recipient or not message:
        return jsonify({"error": "recipient and message required"}), 400
    
    db = next(get_db())
    notification = Notification(
        recipient=recipient,
        type=message_type,
        message=message,
        order_id=order_id,
        status="sent",
        sent_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    
    notification_id = notification.id
    db.close()
    
    return jsonify({"message": "Notification sent", "notification_id": notification_id}), 200

@app.route('/notifications', methods=['GET'])
def list_notifications():
    db = next(get_db())
    notifications = db.query(Notification).all()
    result = [{
        "id": n.id,
        "recipient": n.recipient,
        "type": n.type,
        "message": n.message,
        "status": n.status
    } for n in notifications]
    db.close()
    return jsonify(result), 200

@app.route('/notify/order/<order_id>', methods=['GET'])
def get_notifications_by_order(order_id):
    db = next(get_db())
    notifications = db.query(Notification).filter(Notification.order_id == order_id).all()
    result = [{
        "id": n.id,
        "recipient": n.recipient,
        "message": n.message
    } for n in notifications]
    db.close()
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
