import asyncio
import aiohttp
import time
from performance import perf_monitor

class AsyncAPIClient:
    """Async API client for parallel requests"""
    
    @perf_monitor.measure_async(name="parallel_assign_requests")
    async def parallel_assign_requests(self, num_requests=10):
        """Send multiple assign requests in parallel"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                payload = {
                    "order_id": f"PARALLEL-{i:03d}",
                    "address": f"Test Address {i}",
                    "recipient_phone": f"+7900{i:04d}1234"
                }
                tasks.append(session.post("http://localhost:5001/assign", json=payload))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            results = []
            for i, resp in enumerate(responses):
                if isinstance(resp, Exception):
                    results.append({"index": i, "error": str(resp)})
                else:
                    results.append({"index": i, "status": resp.status})
            
            return results

async def run_performance_test():
    client = AsyncAPIClient()
    
    print("\n" + "="*60)
    print("PERFORMANCE TEST: Parallel Requests")
    print("="*60)
    
    start = time.perf_counter()
    results = await client.parallel_assign_requests(10)
    end = time.perf_counter()
    
    total_time = (end - start) * 1000
    print(f"10 parallel requests completed in {total_time:.2f}ms")
    print(f"Average per request: {total_time/10:.2f}ms")
    
    return total_time

if __name__ == "__main__":
    asyncio.run(run_performance_test())
