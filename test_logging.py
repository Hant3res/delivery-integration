import requests
import time
import json
from api_client import dispatcher_client, tracking_client, notify_client, get_circuit_breaker_status
from logger_config import app_logger, api_logger

def test_success_scenario():
    print("\n" + "="*60)
    print("TEST 1: SUCCESS SCENARIO")
    print("="*60)
    
    app_logger.info("Starting success scenario test")
    
    # Create delivery
    response = requests.post(
        "http://localhost:5001/assign",
        json={"order_id": "LOG-TEST-001", "address": "Moscow", "recipient_phone": "+79001234567"}
    )
    
    if response.status_code == 200:
        data = response.json()
        task_id = data.get("task_id")
        app_logger.info(f"Delivery created: {task_id}")
        print(f"✅ Delivery created: {task_id}")
        
        # Update tracking
        response = requests.post(
            "http://localhost:5002/track/update",
            json={"task_id": task_id, "lat": 55.7558, "lng": 37.6173}
        )
        print(f"✅ Tracking updated: {response.status_code}")
        
        # Complete delivery
        response = requests.post(
            "http://localhost:5002/track/complete",
            json={"task_id": task_id, "proof": "SUCCESS_CODE"}
        )
        print(f"✅ Delivery completed: {response.status_code}")
        
        # Send notification
        response = requests.post(
            "http://localhost:5003/notify",
            json={"recipient": "+79001234567", "message": "Order delivered!", "order_id": "LOG-TEST-001"}
        )
        print(f"✅ Notification sent: {response.status_code}")
    
    app_logger.info("Success scenario completed")

def test_error_scenario():
    print("\n" + "="*60)
    print("TEST 2: ERROR SCENARIO (Wrong endpoint)")
    print("="*60)
    
    app_logger.warning("Starting error scenario test")
    
    # Call non-existent endpoint
    try:
        response = requests.get("http://localhost:5001/non-existent-endpoint")
        print(f"Response: {response.status_code}")
    except Exception as e:
        app_logger.error(f"Error in API call: {str(e)}")
        print(f"❌ Error as expected: {str(e)}")

def test_circuit_breaker_scenario():
    print("\n" + "="*60)
    print("TEST 3: CIRCUIT BREAKER SCENARIO")
    print("="*60)
    
    api_logger.info("Starting circuit breaker test")
    
    for i in range(5):
        try:
            print(f"\nAttempt {i+1}: Calling with circuit breaker...")
            response = dispatcher_client.get("/non-existent-endpoint")
            print(f"Response: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")
            status = get_circuit_breaker_status()
            print(f"Circuit state: {status['dispatcher']['state']}")
            print(f"Failure count: {status['dispatcher']['failure_count']}")
        
        time.sleep(1)

def show_logs():
    print("\n" + "="*60)
    print("RECENT LOGS (last 10 lines from each log)")
    print("="*60)
    
    log_files = ["logs/delivery_app.log", "logs/delivery_api.log"]
    
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                print(f"\n--- {log_file} (last 10 lines) ---")
                for line in lines[-10:]:
                    try:
                        log_json = json.loads(line)
                        print(f"[{log_json['timestamp']}] {log_json['level']}: {log_json['message']}")
                    except:
                        print(line.strip())
        except FileNotFoundError:
            print(f"Log file {log_file} not found")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("LOGGING & ERROR HANDLING DEMO")
    print("="*60)
    
    test_success_scenario()
    test_error_scenario()
    test_circuit_breaker_scenario()
    show_logs()
    
    print("\n" + "="*60)
    print("DEMO COMPLETED")
    print("Check logs/ directory for JSON formatted logs")
    print("="*60)
