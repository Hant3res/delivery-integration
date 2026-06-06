from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import json

class OrderStatus(Enum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    COURIER_ASSIGNED = "COURIER_ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class OrderStateMachine:
    """State machine for order delivery process"""
    
    def __init__(self):
        self.transitions = {
            OrderStatus.NEW: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.COURIER_ASSIGNED, OrderStatus.FAILED],
            OrderStatus.COURIER_ASSIGNED: [OrderStatus.IN_TRANSIT, OrderStatus.FAILED],
            OrderStatus.IN_TRANSIT: [OrderStatus.DELIVERED, OrderStatus.FAILED],
            OrderStatus.DELIVERED: [],
            OrderStatus.FAILED: [OrderStatus.NEW],
            OrderStatus.CANCELLED: []
        }
        self.callbacks: Dict[OrderStatus, list] = {}
    
    def register_callback(self, status: OrderStatus, callback):
        """Register callback for status change"""
        if status not in self.callbacks:
            self.callbacks[status] = []
        self.callbacks[status].append(callback)
    
    def can_transition(self, from_status: OrderStatus, to_status: OrderStatus) -> bool:
        """Check if transition is allowed"""
        if from_status not in self.transitions:
            return False
        return to_status in self.transitions[from_status]
    
    def transition(self, from_status: OrderStatus, to_status: OrderStatus, data: Dict = None) -> Dict:
        """Execute transition from one status to another"""
        if not self.can_transition(from_status, to_status):
            raise ValueError(f"Invalid transition from {from_status.value} to {to_status.value}")
        
        result = {
            "from": from_status.value,
            "to": to_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        }
        
        # Execute callbacks
        if to_status in self.callbacks:
            for callback in self.callbacks[to_status]:
                callback(data)
        
        return result


# Delivery specific state machine
class DeliveryStateMachine:
    """State machine specifically for delivery process"""
    
    def __init__(self):
        self.states = {
            "created": {"order": 1, "next": ["assigned", "cancelled"]},
            "assigned": {"order": 2, "next": ["picked_up", "failed"]},
            "picked_up": {"order": 3, "next": ["in_transit", "failed"]},
            "in_transit": {"order": 4, "next": ["delivered", "failed"]},
            "delivered": {"order": 5, "next": []},
            "failed": {"order": 6, "next": ["retry", "cancelled"]},
            "retry": {"order": 7, "next": ["assigned"]},
            "cancelled": {"order": 8, "next": []}
        }
    
    def get_next_states(self, current_state: str) -> list:
        return self.states.get(current_state, {}).get("next", [])
    
    def can_transition(self, current_state: str, next_state: str) -> bool:
        return next_state in self.get_next_states(current_state)
    
    def get_state_order(self, state: str) -> int:
        return self.states.get(state, {}).get("order", 999)
    
    def is_final_state(self, state: str) -> bool:
        return self.states.get(state, {}).get("next", []) == []
