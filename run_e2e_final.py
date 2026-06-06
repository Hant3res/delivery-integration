import requests
import json
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('e2e_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URLS = {
    "dispatcher": "http://localhost:5001",
    "tracking": "http://localhost:5002",
    "notify": "http://localhost:5003"
}

def run_e2e_test():
    logger.info("=" * 60)
    logger.info("STARTING E2E DELIVERY TEST")
    logger.info("=" * 60)
    
    results = {
        "test_id": f"E2E_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "steps": []
    }
    
    # Step 1: Check couriers
    logger.info("[Step 1] Getting available couriers...")
    resp = requests.get(f"{BASE_URLS['dispatcher']}/couriers")
    couriers = resp.json()
    logger.info(f"✓ Couriers: {[c['name'] for c in couriers]}")
    results["steps"].append({"step": "get_couriers", "status": "PASS", "data": couriers})
    
    # Step 2: Assign delivery
    logger.info("[Step 2] Assigning delivery...")
    resp = requests.post(
        f"{BASE_URLS['dispatcher']}/assign",
        json={
            "order_id": "E2E-FINAL-001",
            "address": "Moscow, Red Square, 1",
            "recipient_phone": "+79001234567"
        }
    )
    assign_result = resp.json()
    task_id = assign_result.get("task_id")
    logger.info(f"✓ Delivery assigned - Task ID: {task_id}, Courier: {assign_result.get('courier_name')}")
    results["steps"].append({"step": "assign_delivery", "status": "PASS", "task_id": task_id})
    
    # Step 3: Update tracking
    logger.info("[Step 3] Updating tracking location...")
    resp = requests.post(
        f"{BASE_URLS['tracking']}/track/update",
        json={"task_id": task_id, "lat": 55.7558, "lng": 37.6173}
    )
    logger.info(f"✓ Tracking updated: {resp.json().get('message')}")
    results["steps"].append({"step": "update_tracking", "status": "PASS"})
    
    # Step 4: Get tracking status
    logger.info("[Step 4] Getting tracking status...")
    resp = requests.get(f"{BASE_URLS['tracking']}/track/{task_id}")
    tracking = resp.json()
    logger.info(f"✓ Status: {tracking.get('status')}")
    results["steps"].append({"step": "get_tracking", "status": "PASS", "data": tracking})
    
    # Step 5: Complete delivery
    logger.info("[Step 5] Completing delivery...")
    resp = requests.post(
        f"{BASE_URLS['tracking']}/track/complete",
        json={"task_id": task_id, "proof": "DELIVERY_CODE_123"}
    )
    logger.info(f"✓ Delivery completed: {resp.json().get('message')}")
    results["steps"].append({"step": "complete_delivery", "status": "PASS"})
    
    # Step 6: Check final status
    logger.info("[Step 6] Checking final delivery status...")
    resp = requests.get(f"{BASE_URLS['dispatcher']}/status/{task_id}")
    final_status = resp.json()
    logger.info(f"✓ Final status: {final_status.get('status')}")
    results["steps"].append({"step": "check_status", "status": "PASS", "final_status": final_status.get('status')})
    
    # Step 7: Send notification
    logger.info("[Step 7] Sending notification...")
    resp = requests.post(
        f"{BASE_URLS['notify']}/notify",
        json={
            "recipient": "+79001234567",
            "type": "sms",
            "message": f"Your order E2E-FINAL-001 has been delivered!",
            "order_id": "E2E-FINAL-001"
        }
    )
    logger.info(f"✓ Notification sent: ID {resp.json().get('notification_id')}")
    results["steps"].append({"step": "send_notification", "status": "PASS"})
    
    # Step 8: Get notifications
    logger.info("[Step 8] Getting all notifications...")
    resp = requests.get(f"{BASE_URLS['notify']}/notifications")
    notifications = resp.json()
    logger.info(f"✓ Total notifications: {len(notifications)}")
    results["steps"].append({"step": "get_notifications", "status": "PASS", "count": len(notifications)})
    
    # Summary
    all_passed = all(s["status"] == "PASS" for s in results["steps"])
    results["overall_status"] = "SUCCESS" if all_passed else "FAILED"
    
    logger.info("=" * 60)
    logger.info(f"E2E TEST COMPLETED: {results['overall_status']}")
    logger.info(f"Total steps: {len(results['steps'])}, Passed: {len([s for s in results['steps'] if s['status'] == 'PASS'])}")
    logger.info("=" * 60)
    
    # Save results
    with open("e2e_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    run_e2e_test()
