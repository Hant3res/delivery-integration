import requests
import json
import logging
import time
from datetime import datetime

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Service URLs
DISPATCHER_URL = "http://localhost:5001"
TRACKING_URL = "http://localhost:5002"
NOTIFY_URL = "http://localhost:5003"

class DeliveryOrchestrator:
    """Integration service orchestrator for delivery process"""
    
    def __init__(self):
        self.delivery_data = {}
        logger.info("Orchestrator initialized")
    
    def assign_delivery(self, order_id, address, recipient_phone):
        """Step 1: Call Dispatcher module to assign courier"""
        logger.info(f"Assigning delivery for order: {order_id}")
        
        payload = {
            "order_id": order_id,
            "address": address,
            "recipient_phone": recipient_phone
        }
        
        try:
            response = requests.post(
                f"{DISPATCHER_URL}/assign",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Delivery assigned successfully: {result}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to assign delivery: {e}")
            raise
    
    def update_tracking(self, task_id, lat, lng):
        """Step 2: Call Tracking module to update courier location"""
        logger.info(f"Updating tracking for task: {task_id}")
        
        payload = {
            "task_id": task_id,
            "lat": lat,
            "lng": lng
        }
        
        try:
            response = requests.post(
                f"{TRACKING_URL}/track/update",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Location updated for task: {task_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update tracking: {e}")
            raise
    
    def get_delivery_status(self, task_id):
        """Step 3: Get delivery status from Tracking module"""
        logger.info(f"Getting status for task: {task_id}")
        
        try:
            response = requests.get(
                f"{TRACKING_URL}/track/{task_id}",
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Status retrieved: {result}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get status: {e}")
            raise
    
    def complete_delivery(self, task_id, proof):
        """Step 4: Complete delivery in Tracking module"""
        logger.info(f"Completing delivery for task: {task_id}")
        
        payload = {
            "task_id": task_id,
            "proof": proof
        }
        
        try:
            response = requests.post(
                f"{TRACKING_URL}/track/complete",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Delivery completed for task: {task_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to complete delivery: {e}")
            raise
    
    def send_notification(self, recipient, message, order_id, notification_type="sms"):
        """Step 5: Send notification via Notify module"""
        logger.info(f"Sending notification to: {recipient}")
        
        payload = {
            "recipient": recipient,
            "type": notification_type,
            "message": message,
            "order_id": order_id
        }
        
        try:
            response = requests.post(
                f"{NOTIFY_URL}/notify",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Notification sent to: {recipient}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send notification: {e}")
            raise
    
    def full_delivery_workflow(self, order_id, address, recipient_phone):
        """Complete workflow: assign -> track -> notify -> complete"""
        logger.info(f"Starting full delivery workflow for order: {order_id}")
        
        # Step 1: Assign courier
        assign_result = self.assign_delivery(order_id, address, recipient_phone)
        task_id = assign_result.get('task_id')
        courier_name = assign_result.get('courier_name')
        
        if not task_id:
            logger.error("No task_id returned from dispatcher")
            return {"error": "Failed to assign delivery"}
        
        # Step 2: Send notification about assignment
        self.send_notification(
            recipient_phone,
            f"Your order {order_id} has been assigned to courier {courier_name}",
            order_id,
            "sms"
        )
        
        # Step 3: Simulate tracking updates
        import random
        locations = [
            (55.7558, 37.6173),  # Red Square
            (55.7600, 37.6200),  # En route
            (55.7650, 37.6250)   # Near destination
        ]
        
        for lat, lng in locations:
            self.update_tracking(task_id, lat, lng)
            time.sleep(1)
        
        # Step 4: Get current status
        status = self.get_delivery_status(task_id)
        
        # Step 5: Complete delivery
        complete_result = self.complete_delivery(task_id, "delivery_code_123")
        
        # Step 6: Send completion notification
        self.send_notification(
            recipient_phone,
            f"Your order {order_id} has been delivered successfully!",
            order_id,
            "sms"
        )
        
        logger.info(f"Workflow completed for order: {order_id}")
        return {
            "order_id": order_id,
            "task_id": task_id,
            "courier_name": courier_name,
            "status": "completed",
            "tracking_updates": len(locations),
            "result": complete_result
        }


# Main execution
if __name__ == "__main__":
    orchestrator = DeliveryOrchestrator()
    
    # Test workflow
    result = orchestrator.full_delivery_workflow(
        order_id="ORD-INTEGRATION-001",
        address="Moscow, Red Square, 1",
        recipient_phone="+79001234567"
    )
    
    print("\n" + "="*50)
    print("WORKFLOW RESULT:")
    print(json.dumps(result, indent=2))
    print("="*50)
