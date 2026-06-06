import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import Courier, Delivery, TrackingHistory, Notification

class TestModels(unittest.TestCase):
    """Unit tests for data models"""
    
    def test_courier_creation(self):
        """Test Courier model creation"""
        courier = Courier(
            courier_id="test_001",
            name="Test Courier",
            available=True,
            location="Moscow"
        )
        self.assertEqual(courier.courier_id, "test_001")
        self.assertEqual(courier.name, "Test Courier")
        self.assertTrue(courier.available)
        self.assertEqual(courier.location, "Moscow")
    
    def test_delivery_creation(self):
        """Test Delivery model creation"""
        delivery = Delivery(
            task_id="task_001",
            order_id="order_001",
            address="Test Address",
            recipient_phone="+79001234567",
            courier_id="courier_001",
            courier_name="Test Courier",
            status="assigned"
        )
        self.assertEqual(delivery.task_id, "task_001")
        self.assertEqual(delivery.order_id, "order_001")
        self.assertEqual(delivery.status, "assigned")
    
    def test_delivery_status_transition(self):
        """Test delivery status transitions"""
        delivery = Delivery(
            task_id="task_002",
            order_id="order_002",
            address="Test Address",
            recipient_phone="+79001234567",
            status="assigned"
        )
        
        # Simulate status transition
        delivery.status = "in_transit"
        self.assertEqual(delivery.status, "in_transit")
        
        delivery.status = "delivered"
        self.assertEqual(delivery.status, "delivered")
    
    def test_tracking_history_creation(self):
        """Test TrackingHistory model creation"""
        from datetime import datetime
        tracking = TrackingHistory(
            task_id="task_001",
            lat=55.7558,
            lng=37.6173,
            status="in_transit"
        )
        self.assertEqual(tracking.task_id, "task_001")
        self.assertEqual(tracking.lat, 55.7558)
        self.assertEqual(tracking.lng, 37.6173)
    
    def test_notification_creation(self):
        """Test Notification model creation"""
        notification = Notification(
            recipient="+79001234567",
            type="sms",
            message="Test message",
            order_id="order_001",
            status="sent"
        )
        self.assertEqual(notification.recipient, "+79001234567")
        self.assertEqual(notification.type, "sms")
        self.assertEqual(notification.status, "sent")

if __name__ == '__main__':
    unittest.main()
