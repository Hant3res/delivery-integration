import requests
import time
import json

def benchmark_couriers():
    """Benchmark GET /couriers endpoint"""
    print("\n--- Benchmark: GET /couriers ---")
    
    # First request (cache miss)
    start = time.perf_counter()
    response = requests.get("http://localhost:5001/couriers")
    first = (time.perf_counter() - start) * 1000
    
    # Second request (cache hit)
    start = time.perf_counter()
    response = requests.get("http://localhost:5001/couriers")
    second = (time.perf_counter() - start) * 1000
    
    print(f"   First request (cache miss): {first:.2f}ms")
    print(f"   Second request (cache hit): {second:.2f}ms")
    print(f"   Improvement: {(first - second) / first * 100:.1f}% faster")
    
    return {"first": first, "second": second}

def benchmark_assign_delivery():
    """Benchmark POST /assign endpoint"""
    print("\n--- Benchmark: POST /assign ---")
    
    times = []
    for i in range(5):
        start = time.perf_counter()
        response = requests.post(
            "http://localhost:5001/assign",
            json={
                "order_id": f"BENCH-{i:03d}",
                "address": "Moscow, Test Address",
                "recipient_phone": f"+7900{i:04d}1234"
            }
        )
        times.append((time.perf_counter() - start) * 1000)
    
    avg = sum(times) / len(times)
    print(f"   Average: {avg:.2f}ms")
    print(f"   Min: {min(times):.2f}ms, Max: {max(times):.2f}ms")
    
    return {"avg": avg, "min": min(times), "max": max(times)}

def benchmark_tracking_update():
    """Benchmark POST /track/update"""
    print("\n--- Benchmark: POST /track/update ---")
    
    # First create a delivery to get task_id
    resp = requests.post(
        "http://localhost:5001/assign",
        json={"order_id": "TRACK-BENCH", "address": "Moscow", "recipient_phone": "+79009999999"}
    )
    if resp.status_code != 200:
        print("   ⚠ Could not create delivery for tracking test")
        return None
    
    task_id = resp.json()["task_id"]
    
    times = []
    for i in range(5):
        start = time.perf_counter()
        response = requests.post(
            "http://localhost:5002/track/update",
            json={"task_id": task_id, "lat": 55.7558, "lng": 37.6173}
        )
        times.append((time.perf_counter() - start) * 1000)
    
    avg = sum(times) / len(times)
    print(f"   Average: {avg:.2f}ms")
    
    return {"avg": avg}

def benchmark_complete_delivery():
    """Benchmark POST /track/complete"""
    print("\n--- Benchmark: POST /track/complete ---")
    
    # First create a delivery
    resp = requests.post(
        "http://localhost:5001/assign",
        json={"order_id": "COMPLETE-BENCH", "address": "Moscow", "recipient_phone": "+79008888888"}
    )
    if resp.status_code != 200:
        print("   ⚠ Could not create delivery for complete test")
        return None
    
    task_id = resp.json()["task_id"]
    
    times = []
    for i in range(3):
        start = time.perf_counter()
        response = requests.post(
            "http://localhost:5002/track/complete",
            json={"task_id": task_id, "proof": f"BENCH_{i}"}
        )
        times.append((time.perf_counter() - start) * 1000)
    
    avg = sum(times) / len(times)
    print(f"   Average: {avg:.2f}ms")
    
    return {"avg": avg}

def benchmark_notify():
    """Benchmark POST /notify"""
    print("\n--- Benchmark: POST /notify ---")
    
    times = []
    for i in range(5):
        start = time.perf_counter()
        response = requests.post(
            "http://localhost:5003/notify",
            json={
                "recipient": "+79007777777",
                "type": "sms",
                "message": f"Benchmark notification {i}",
                "order_id": "BENCH-NOTIFY"
            }
        )
        times.append((time.perf_counter() - start) * 1000)
    
    avg = sum(times) / len(times)
    print(f"   Average: {avg:.2f}ms")
    
    return {"avg": avg}

if __name__ == "__main__":
    print("="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    print("\n⚠ Make sure all modules are running!")
    print("  - Dispatcher: http://localhost:5001")
    print("  - Tracking: http://localhost:5002")  
    print("  - Notify: http://localhost:5003")
    
    try:
        # Check services
        requests.get("http://localhost:5001/couriers", timeout=2)
        print("\n✓ Services are running")
    except:
        print("\n✗ Services are NOT running. Start them first!")
        print("  python module_a_dispatcher.py &")
        print("  python module_b_tracking.py &")
        print("  python module_c_notify.py &")
        exit(1)
    
    # Run benchmarks
    courier_results = benchmark_couriers()
    assign_results = benchmark_assign_delivery()
    tracking_results = benchmark_tracking_update()
    complete_results = benchmark_complete_delivery()
    notify_results = benchmark_notify()
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    print(f"\n📊 GET /couriers:")
    print(f"   Without cache: {courier_results['first']:.2f}ms")
    print(f"   With cache:    {courier_results['second']:.2f}ms")
    improvement = (courier_results['first'] - courier_results['second']) / courier_results['first'] * 100
    print(f"   ✅ Improvement: {improvement:.1f}% faster")
    
    print(f"\n📊 POST /assign (write operation):")
    print(f"   Average: {assign_results['avg']:.2f}ms")
    
    if tracking_results:
        print(f"\n📊 POST /track/update:")
        print(f"   Average: {tracking_results['avg']:.2f}ms")
    
    if complete_results:
        print(f"\n📊 POST /track/complete (with courier release):")
        print(f"   Average: {complete_results['avg']:.2f}ms")
    
    print(f"\n📊 POST /notify:")
    print(f"   Average: {notify_results['avg']:.2f}ms")
    
    print("\n" + "="*60)
    print("✅ BENCHMARK COMPLETED")
    print("="*60)
