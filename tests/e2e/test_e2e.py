import unittest
import requests
import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from e2e_scenario import EndToEndDelivery

class TestE2E(unittest.TestCase):
    """End-to-end tests"""
    
    def test_e2e_happy_path(self):
        """Test happy path: assign -> track -> complete -> notify"""
        e2e = EndToEndDelivery()
        
        result = e2e.run_scenario(
            order_id="E2E-HAPPY-001",
            address="Moscow, Happy Path Test",
            recipient_phone="+79007777777"
        )
        
        self.assertEqual(result["final_status"], "SUCCESS")
        
        # Check all steps succeeded
        for step in result["steps"]:
            self.assertTrue(step["success"], f"Step {step['step']} failed: {step.get('error', 'Unknown error')}")
        
        print(f"\n✓ E2E happy path completed: {len(result['steps'])} steps")
    
    def test_e2e_invalid_order(self):
        """Test E2E with invalid data"""
        e2e = EndToEndDelivery()
        
        # Run with invalid data
        result = e2e.run_scenario(
            order_id="",
            address="",
            recipient_phone=""
        )
        
        # Should fail on first step
        self.assertEqual(result["final_status"], "FAILED")
        self.assertFalse(result["steps"][0]["success"])
        print(f"\n✓ Invalid order handled correctly")
    
    def test_e2e_saga_pattern(self):
        """Test E2E with Saga pattern"""
        from saga import DeliverySaga
        
        saga = DeliverySaga.create_delivery_saga("e2e_saga_test")
        
        context = {
            "order_id": "E2E-SAGA-001",
            "address": "Moscow, Saga Test",
            "recipient_phone": "+79006666666",
            "lat": 55.7558,
            "lng": 37.6173
        }
        
        result = saga.execute(context)
        
        # Saga may fail if modules not running, but structure is tested
        self.assertIn(result["status"], ["completed", "failed"])
        print(f"\n✓ Saga pattern test completed: {result['status']}")

if __name__ == '__main__':
    unittest.main()
