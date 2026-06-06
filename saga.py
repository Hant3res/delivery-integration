import logging
from typing import Dict, Any, List, Callable
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SagaStep:
    """Single step in Saga transaction"""
    
    def __init__(self, name: str, action: Callable, compensation: Callable):
        self.name = name
        self.action = action
        self.compensation = compensation
        self.completed = False
        self.result = None

class SagaOrchestrator:
    """Saga pattern orchestrator for distributed transactions"""
    
    def __init__(self, saga_id: str = None):
        self.saga_id = saga_id or f"saga_{datetime.utcnow().timestamp()}"
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []
        self.status = "pending"  # pending, executing, completed, compensating, failed
    
    def add_step(self, name: str, action: Callable, compensation: Callable) -> 'SagaOrchestrator':
        """Add a step to the saga"""
        self.steps.append(SagaStep(name, action, compensation))
        return self
    
    def execute(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute all saga steps with compensation on failure"""
        context = context or {}
        self.status = "executing"
        logger.info(f"Saga {self.saga_id}: Starting execution")
        
        for step in self.steps:
            try:
                logger.info(f"Saga {self.saga_id}: Executing step '{step.name}'")
                step.result = step.action(context)
                step.completed = True
                self.completed_steps.append(step)
                context[f"step_{step.name}_result"] = step.result
            except Exception as e:
                logger.error(f"Saga {self.saga_id}: Step '{step.name}' failed: {e}")
                self._compensate()
                self.status = "failed"
                return {
                    "saga_id": self.saga_id,
                    "status": "failed",
                    "failed_step": step.name,
                    "error": str(e)
                }
        
        self.status = "completed"
        logger.info(f"Saga {self.saga_id}: Completed successfully")
        return {
            "saga_id": self.saga_id,
            "status": "completed",
            "result": context
        }
    
    def _compensate(self):
        """Execute compensation for completed steps in reverse order"""
        self.status = "compensating"
        logger.info(f"Saga {self.saga_id}: Starting compensation")
        
        for step in reversed(self.completed_steps):
            try:
                logger.info(f"Saga {self.saga_id}: Compensating step '{step.name}'")
                step.compensation(step.result)
            except Exception as e:
                logger.error(f"Saga {self.saga_id}: Compensation for '{step.name}' failed: {e}")


# Delivery Saga specific implementation
class DeliverySaga:
    """Saga for delivery process"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    @staticmethod
    def create_delivery_saga(saga_id: str = None):
        """Factory method to create a delivery saga"""
        
        def assign_courier_action(context):
            # Call dispatcher module
            import requests
            response = requests.post(
                "http://localhost:5001/assign",
                json={
                    "order_id": context.get("order_id"),
                    "address": context.get("address"),
                    "recipient_phone": context.get("recipient_phone")
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        def assign_courier_compensation(result):
            # Release courier (mark as available again)
            # In real system, would call API to release courier
            logger.info(f"Compensating: Releasing courier {result.get('courier_id')}")
        
        def update_tracking_action(context):
            import requests
            task_id = context.get("step_assign_courier_result", {}).get("task_id")
            response = requests.post(
                "http://localhost:5002/track/update",
                json={
                    "task_id": task_id,
                    "lat": context.get("lat", 55.7558),
                    "lng": context.get("lng", 37.6173)
                },
                timeout=10
            )
            response.raise_for_status()
            return {"status": "tracking_updated", "task_id": task_id}
        
        def update_tracking_compensation(result):
            logger.info(f"Compensating: Removing tracking for {result.get('task_id')}")
        
        def send_notification_action(context):
            import requests
            response = requests.post(
                "http://localhost:5003/notify",
                json={
                    "recipient": context.get("recipient_phone"),
                    "type": "sms",
                    "message": f"Your order {context.get('order_id')} is being processed",
                    "order_id": context.get("order_id")
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        def send_notification_compensation(result):
            logger.info(f"Compensating: Removing notification {result.get('notification_id')}")
        
        saga = SagaOrchestrator(saga_id)
        saga.add_step("assign_courier", assign_courier_action, assign_courier_compensation)
        saga.add_step("update_tracking", update_tracking_action, update_tracking_compensation)
        saga.add_step("send_notification", send_notification_action, send_notification_compensation)
        
        return saga
