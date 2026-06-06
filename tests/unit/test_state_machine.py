import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from state_machine import DeliveryStateMachine, OrderStateMachine, OrderStatus

class TestStateMachine(unittest.TestCase):
    """Unit tests for state machines"""
    
    def setUp(self):
        self.delivery_sm = DeliveryStateMachine()
        self.order_sm = OrderStateMachine()
    
    def test_delivery_state_transitions(self):
        """Test valid delivery state transitions"""
        # Valid transitions
        self.assertTrue(self.delivery_sm.can_transition("created", "assigned"))
        self.assertTrue(self.delivery_sm.can_transition("assigned", "picked_up"))
        self.assertTrue(self.delivery_sm.can_transition("picked_up", "in_transit"))
        self.assertTrue(self.delivery_sm.can_transition("in_transit", "delivered"))
        
        # Invalid transitions
        self.assertFalse(self.delivery_sm.can_transition("created", "delivered"))
        self.assertFalse(self.delivery_sm.can_transition("assigned", "delivered"))
    
    def test_delivery_next_states(self):
        """Test getting next possible states"""
        next_states = self.delivery_sm.get_next_states("created")
        self.assertIn("assigned", next_states)
        self.assertIn("cancelled", next_states)
        
        next_states = self.delivery_sm.get_next_states("delivered")
        self.assertEqual(next_states, [])
    
    def test_delivery_state_order(self):
        """Test state order"""
        self.assertEqual(self.delivery_sm.get_state_order("created"), 1)
        self.assertEqual(self.delivery_sm.get_state_order("assigned"), 2)
        self.assertEqual(self.delivery_sm.get_state_order("picked_up"), 3)
        self.assertEqual(self.delivery_sm.get_state_order("in_transit"), 4)
        self.assertEqual(self.delivery_sm.get_state_order("delivered"), 5)
    
    def test_is_final_state(self):
        """Test final state detection"""
        self.assertTrue(self.delivery_sm.is_final_state("delivered"))
        self.assertTrue(self.delivery_sm.is_final_state("cancelled"))
        self.assertFalse(self.delivery_sm.is_final_state("created"))
    
    def test_order_state_transitions(self):
        """Test order state machine transitions"""
        # Valid transition
        result = self.order_sm.transition(OrderStatus.NEW, OrderStatus.PROCESSING)
        self.assertEqual(result["from"], "NEW")
        self.assertEqual(result["to"], "PROCESSING")
        
        # Invalid transition
        with self.assertRaises(ValueError):
            self.order_sm.transition(OrderStatus.NEW, OrderStatus.DELIVERED)

if __name__ == '__main__':
    unittest.main()
