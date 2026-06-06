from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db, get_db, Courier, Delivery
from logger_config import app_logger, log_with_props

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/assign', methods=['POST'])
def assign_delivery():
    request_id = str(uuid.uuid4())[:8]
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        address = data.get('address')
        recipient_phone = data.get('recipient_phone')
        
        log_with_props(app_logger, logging.INFO, 
            f"Assign delivery request received",
            request_id=request_id,
            order_id=order_id,
            address=address
        )
        
        if not order_id or not address:
            app_logger.warning(f"Missing required fields: order_id={order_id}, address={address}")
            return jsonify({"error": "order_id and address required"}), 400
        
        db = next(get_db())
        courier = db.query(Courier).filter(Courier.available == True).first()
        
        if not courier:
            app_logger.warning(f"No available couriers for order {order_id}")
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
            status="assigned"
        )
        db.add(delivery)
        db.commit()
        db.close()
        
        log_with_props(app_logger, logging.INFO,
            f"Delivery assigned successfully",
            request_id=request_id,
            task_id=task_id,
            courier_id=courier_id,
            courier_name=courier_name
        )
        
        return jsonify({
            "task_id": task_id,
            "courier_id": courier_id,
            "courier_name": courier_name,
            "status": "assigned"
        }), 200
        
    except Exception as e:
        app_logger.error(f"Error in assign_delivery: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    try:
        app_logger.info(f"Getting status for task: {task_id}")
        
        db = next(get_db())
        delivery = db.query(Delivery).filter(Delivery.task_id == task_id).first()
        if not delivery:
            db.close()
            app_logger.warning(f"Task not found: {task_id}")
            return jsonify({"error": "Task not found"}), 404
        
        result = {
            "task_id": delivery.task_id,
            "order_id": delivery.order_id,
            "status": delivery.status,
            "courier_name": delivery.courier_name
        }
        db.close()
        return jsonify(result), 200
        
    except Exception as e:
        app_logger.error(f"Error getting status for {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/couriers', methods=['GET'])
def list_couriers():
    try:
        app_logger.info("Listing all couriers")
        
        db = next(get_db())
        couriers = db.query(Courier).all()
        result = [{
            "id": c.courier_id,
            "name": c.name,
            "available": c.available,
            "location": c.location
        } for c in couriers]
        db.close()
        
        app_logger.info(f"Returned {len(result)} couriers")
        return jsonify(result), 200
        
    except Exception as e:
        app_logger.error(f"Error listing couriers: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/deliveries', methods=['GET'])
def list_deliveries():
    try:
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
    except Exception as e:
        app_logger.error(f"Error listing deliveries: {str(e)}")
        return jsonify({"error": str(e)}), 500

import logging
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
