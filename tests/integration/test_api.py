import unittest
import requests
import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BASE_URLS = {
    "dispatcher": "http://localhost:5001",
    "tracking": "http://localhost:5002",
    "notify": "http://localhost:5003"
}

class TestIntegrationAPI(unittest.TestCase):
    """Integration tests for all modules"""
    
    @classmethod
    def setUpClass(cls):
        """Check if services are running"""
        print("\nChecking services...")
        for name, url in BASE_URLS.items():
            try:
                response = requests.get(f"{url}/couriers" if name == "dispatcher" else f"{url}/notifications")
                print(f"✓ {name} service is running")
            except:
                print(f"✗ {name} service is NOT running - tests may fail")
    
    def test_01_dispatcher_couriers(self):
        """Test dispatcher - get couriers list"""
        response = requests.get(f"{BASE_URLS['dispatcher']}/couriers")
        self.assertEqual(response.status_code, 200)
        
        couriers = response.json()
        self.assertIsInstance(couriers, list)
        if len(couriers) > 0:
            self.assertIn("id", couriers[0])
            self.assertIn("name", couriers[0])
            self.assertIn("available", couriers[0])
        
        print(f"✓ Got {len(couriers)} couriers")
    
    def test_02_dispatcher_assign_delivery(self):
        """Test dispatcher - assign delivery"""
        payload = {
            "order_id": "INT-TEST-001",
            "address": "Moscow, Test Address",
            "recipient_phone": "+79009999999"
        }
        
        response = requests.post(
            f"{BASE_URLS['dispatcher']}/assign",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("task_id", data)
        self.assertIn("courier_name", data)
        
        # Store task_id for other tests
        self.__class__.task_id = data["task_id"]
        print(f"✓ Delivery assigned: {data['task_id']}")
    
    def test_03_dispatcher_deliveries(self):
        """Test dispatcher - get deliveries list"""
        response = requests.get(f"{BASE_URLS['dispatcher']}/deliveries")
        self.assertEqual(response.status_code, 200)
        
        deliveries = response.json()
        self.assertIsInstance(deliveries, list)
        print(f"✓ Got {len(deliveries)} deliveries")
    
    def test_04_tracking_update(self):
        """Test tracking - update location"""
        if not hasattr(self.__class__, 'task_id'):
            self.skipTest("No task_id available")
        
        payload = {
            "task_id": self.__class__.task_id,
            "lat": 55.7558,
            "lng": 37.6173
        }
        
        response = requests.post(
            f"{BASE_URLS['tracking']}/track/update",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        print(f"✓ Location updated for {self.__class__.task_id}")
    
    def test_05_tracking_status(self):
        """Test tracking - get delivery status"""
        if not hasattr(self.__class__, 'task_id'):
            self.skipTest("No task_id available")
        
        response = requests.get(f"{BASE_URLS['tracking']}/track/{self.__class__.task_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("task_id", data)
        self.assertIn("status", data)
        print(f"✓ Status: {data['status']}")
    
    def test_06_tracking_complete(self):
        """Test tracking - complete delivery"""
        if not hasattr(self.__class__, 'task_id'):
            self.skipTest("No task_id available")
        
        payload = {
            "task_id": self.__class__.task_id,
            "proof": "INTEGRATION_TEST_PROOF"
        }
        
        response = requests.post(
            f"{BASE_URLS['tracking']}/track/complete",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        print(f"✓ Delivery completed for {self.__class__.task_id}")
    
    def test_07_notify_send(self):
        """Test notify - send notification"""
        payload = {
            "recipient": "+79009999999",
            "type": "sms",
            "message": "Integration test notification",
            "order_id": "INT-TEST-001"
        }
        
        response = requests.post(
            f"{BASE_URLS['notify']}/notify",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("notification_id", data)
        print(f"✓ Notification sent: ID {data['notification_id']}")
    
    def test_08_notify_list(self):
        """Test notify - list notifications"""
        response = requests.get(f"{BASE_URLS['notify']}/notifications")
        self.assertEqual(response.status_code, 200)
        
        notifications = response.json()
        self.assertIsInstance(notifications, list)
        print(f"✓ Got {len(notifications)} notifications")
    
    def test_09_full_workflow(self):
        """Test full workflow - create, track, complete, notify"""
        # Create delivery
        payload = {
            "order_id": "INT-WORKFLOW-001",
            "address": "Moscow, Full Workflow Test",
            "recipient_phone": "+79008888888"
        }
        
        response = requests.post(f"{BASE_URLS['dispatcher']}/assign", json=payload)
        self.assertEqual(response.status_code, 200)
        task_id = response.json()["task_id"]
        
        # Update tracking
        response = requests.post(
            f"{BASE_URLS['tracking']}/track/update",
            json={"task_id": task_id, "lat": 55.7558, "lng": 37.6173}
        )
        self.assertEqual(response.status_code, 200)
        
        # Complete delivery
        response = requests.post(
            f"{BASE_URLS['tracking']}/track/complete",
            json={"task_id": task_id, "proof": "WORKFLOW_PROOF"}
        )
        self.assertEqual(response.status_code, 200)
        
        # Send notification
        response = requests.post(
            f"{BASE_URLS['notify']}/notify",
            json={
                "recipient": "+79008888888",
                "type": "sms",
                "message": "Your order has been delivered!",
                "order_id": "INT-WORKFLOW-001"
            }
        )
        self.assertEqual(response.status_code, 200)
        
        print(f"✓ Full workflow completed for {task_id}")

if __name__ == '__main__':
    unittest.main()
