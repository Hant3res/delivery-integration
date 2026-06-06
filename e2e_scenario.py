import requests
import time
import json
import logging
from datetime import datetime
from state_machine import DeliveryStateMachine, OrderStatus, OrderStateMachine
from saga import DeliverySaga

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EndToEndDelivery:
    """End-to-end delivery scenario orchestrator"""
    
    def __init__(self):
        self.dispatcher_url = "http://localhost:5001"
        self.tracking_url = "http://localhost:5002"
        self.notify_url = "http://localhost:5003"
        self.state_machine = DeliveryStateMachine()
        self.order_state_machine = OrderStateMachine()
        self.current_status = "created"
        self.order_status = OrderStatus.NEW
        self.task_id = None
        self.courier = None
    
    def run_scenario(self, order_id: str, address: str, recipient_phone: str) -> dict:
        """Run complete end-to-end delivery scenario"""
        
        logger.info("=" * 60)
        logger.info(f"STARTING E2E SCENARIO: Order {order_id}")
        logger.info("=" * 60)
        
        result = {
            "order_id": order_id,
            "start_time": datetime.utcnow().isoformat(),
            "steps": []
        }
        
        # Step 1: Assign courier
        step1 = self._assign_courier(order_id, address, recipient_phone)
        result["steps"].append(step1)
        if not step1["success"]:
            return self._finalize_result(result, False)
        
        # Step 2: Update order state to PROCESSING
        step2 = self._update_order_state(OrderStatus.PROCESSING)
        result["steps"].append(step2)
        
        # Step 3: Update tracking (in transit)
        step3 = self._update_tracking(self.task_id, 55.7558, 37.6173)
        result["steps"].append(step3)
        
        # Step 4: Update order state to IN_TRANSIT
        step4 = self._update_order_state(OrderStatus.IN_TRANSIT)
        result["steps"].append(step4)
        
        # Step 5: Complete delivery
        step5 = self._complete_delivery(self.task_id, "DELIVERY_CODE_123")
        result["steps"].append(step5)
        
        # Step 6: Update order state to DELIVERED
        step6 = self._update_order_state(OrderStatus.DELIVERED)
        result["steps"].append(step6)
        
        # Step 7: Send completion notification
        step7 = self._send_notification(recipient_phone, order_id, "delivered")
        result["steps"].append(step7)
        
        result["end_time"] = datetime.utcnow().isoformat()
        result["final_status"] = "SUCCESS" if all(s["success"] for s in result["steps"]) else "FAILED"
        
        logger.info("=" * 60)
        logger.info(f"E2E SCENARIO COMPLETED: {result['final_status']}")
        logger.info("=" * 60)
        
        return result
    
    def _assign_courier(self, order_id, address, recipient_phone):
        logger.info(f"[Step 1] Assigning courier for order {order_id}")
        
        try:
            response = requests.post(
                f"{self.dispatcher_url}/assign",
                json={
                    "order_id": order_id,
                    "address": address,
                    "recipient_phone": recipient_phone
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.task_id = data.get("task_id")
            self.courier = data.get("courier_name")
            self.current_status = "assigned"
            
            logger.info(f"[Step 1] SUCCESS - Task ID: {self.task_id}, Courier: {self.courier}")
            return {"step": "assign_courier", "success": True, "task_id": self.task_id, "courier": self.courier}
        except Exception as e:
            logger.error(f"[Step 1] FAILED - {e}")
            return {"step": "assign_courier", "success": False, "error": str(e)}
    
    def _update_tracking(self, task_id, lat, lng):
        logger.info(f"[Step 3] Updating tracking for task {task_id}")
        
        try:
            response = requests.post(
                f"{self.tracking_url}/track/update",
                json={"task_id": task_id, "lat": lat, "lng": lng},
                timeout=10
            )
            response.raise_for_status()
            self.current_status = "in_transit"
            logger.info(f"[Step 3] SUCCESS - Location updated")
            return {"step": "update_tracking", "success": True}
        except Exception as e:
            logger.error(f"[Step 3] FAILED - {e}")
            return {"step": "update_tracking", "success": False, "error": str(e)}
    
    def _complete_delivery(self, task_id, proof):
        logger.info(f"[Step 5] Completing delivery for task {task_id}")
        
        try:
            response = requests.post(
                f"{self.tracking_url}/track/complete",
                json={"task_id": task_id, "proof": proof},
                timeout=10
            )
            response.raise_for_status()
            self.current_status = "delivered"
            logger.info(f"[Step 5] SUCCESS - Delivery completed")
            return {"step": "complete_delivery", "success": True}
        except Exception as e:
            logger.error(f"[Step 5] FAILED - {e}")
            return {"step": "complete_delivery", "success": False, "error": str(e)}
    
    def _send_notification(self, recipient, order_id, status):
        logger.info(f"[Step 7] Sending notification to {recipient}")
        
        try:
            response = requests.post(
                f"{self.notify_url}/notify",
                json={
                    "recipient": recipient,
                    "type": "sms",
                    "message": f"Your order {order_id} has been {status}!",
                    "order_id": order_id
                },
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"[Step 7] SUCCESS - Notification sent")
            return {"step": "send_notification", "success": True}
        except Exception as e:
            logger.error(f"[Step 7] FAILED - {e}")
            return {"step": "send_notification", "success": False, "error": str(e)}
    
    def _update_order_state(self, new_status: OrderStatus):
        logger.info(f"[State] Transitioning from {self.order_status.value} to {new_status.value}")
        
        try:
            transition = self.order_state_machine.transition(self.order_status, new_status)
            self.order_status = new_status
            return {"step": "update_order_state", "success": True, "transition": transition}
        except ValueError as e:
            logger.error(f"[State] Invalid transition: {e}")
            return {"step": "update_order_state", "success": False, "error": str(e)}
    
    def _finalize_result(self, result, success):
        result["end_time"] = datetime.utcnow().isoformat()
        result["final_status"] = "SUCCESS" if success else "FAILED"
        return result


def run_e2e_with_saga():
    """Run E2E scenario using Saga pattern"""
    logger.info("Starting E2E scenario with Saga pattern")
    
    saga = DeliverySaga.create_delivery_saga("delivery_e2e_001")
    
    context = {
        "order_id": "E2E-SAGA-001",
        "address": "Moscow, Red Square",
        "recipient_phone": "+79001234567",
        "lat": 55.7558,
        "lng": 37.6173
    }
    
    result = saga.execute(context)
    logger.info(f"Saga result: {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    # Simple E2E scenario
    e2e = EndToEndDelivery()
    result = e2e.run_scenario(
        order_id="E2E-TEST-001",
        address="Moscow, Red Square, 1",
        recipient_phone="+79001234567"
    )
    
    print("\n" + "=" * 60)
    print("E2E SCENARIO RESULT:")
    print(json.dumps(result, indent=2, default=str))
    print("=" * 60)
    
    # Run with Saga
    print("\n" + "=" * 60)
    run_e2e_with_saga()
    print("=" * 60)
