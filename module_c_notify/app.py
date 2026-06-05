from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
import random

app = Flask(__name__)

notifications_queue = []
sent_notifications = []

def worker():
    while True:
        if notifications_queue:
            notif = notifications_queue.pop(0)
            time.sleep(1)
            notif['sent_at'] = datetime.now().isoformat()
            notif['status'] = 'sent'
            sent_notifications.append(notif)
            print(f"[NOTIFY] Отправлено: {notif['type']} -> {notif['recipient']}")
        time.sleep(0.5)

thread = threading.Thread(target=worker, daemon=True)
thread.start()

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.get_json()
    recipient = data.get('recipient')
    message_type = data.get('type')
    message = data.get('message')
    order_id = data.get('order_id')
    
    if not recipient or not message:
        return jsonify({"error": "recipient and message required"}), 400
    
    notification = {
        "id": random.randint(1000, 9999),
        "recipient": recipient,
        "type": message_type or "sms",
        "message": message,
        "order_id": order_id,
        "queued_at": datetime.now().isoformat(),
        "status": "queued"
    }
    
    notifications_queue.append(notification)
    
    return jsonify({
        "message": "Notification queued",
        "notification_id": notification['id'],
        "status": "queued"
    }), 202

@app.route('/notifications', methods=['GET'])
def list_notifications():
    return jsonify({
        "queued": notifications_queue,
        "sent": sent_notifications
    }), 200

@app.route('/notify/demo/order-status', methods=['POST'])
def demo_order_notification():
    data = request.get_json()
    phone = data.get('phone')
    order_id = data.get('order_id')
    status = data.get('status')
    
    message = f"Заказ #{order_id} теперь в статусе: {status}"
    
    return send_notification()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
