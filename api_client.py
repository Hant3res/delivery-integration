import requests
import time
import json
import logging
from resilience import retry, circuit_breakers, get_circuit_breaker_status
from logger_config import api_logger, log_with_props

class APIClient:
    """API Client with retry and circuit breaker"""
    
    def __init__(self, base_url, service_name):
        self.base_url = base_url
        self.service_name = service_name
        self.circuit_breaker = circuit_breakers.get(service_name)
    
    @retry(max_attempts=3, delay=1, backoff=2)
    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        log_with_props(api_logger, logging.INFO,
            f"Making {method} request to {url}",
            service=self.service_name,
            endpoint=endpoint
        )
        
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            
            log_with_props(api_logger, logging.INFO,
                f"Response from {url}: {response.status_code}",
                service=self.service_name,
                status_code=response.status_code
            )
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout as e:
            api_logger.error(f"Timeout error calling {url}: {str(e)}")
            raise
            
        except requests.exceptions.ConnectionError as e:
            api_logger.error(f"Connection error calling {url}: {str(e)}")
            raise
            
        except requests.exceptions.HTTPError as e:
            api_logger.error(f"HTTP error calling {url}: {e.response.status_code} - {e.response.text}")
            raise
    
    def call_with_circuit_breaker(self, method, endpoint, **kwargs):
        """Call API with circuit breaker protection"""
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                self._make_request, method, endpoint, **kwargs
            )
        else:
            return self._make_request(method, endpoint, **kwargs)
    
    def post(self, endpoint, json=None, headers=None):
        return self.call_with_circuit_breaker("POST", endpoint, json=json, headers=headers)
    
    def get(self, endpoint, headers=None):
        return self.call_with_circuit_breaker("GET", endpoint, headers=headers)
    
    def put(self, endpoint, json=None, headers=None):
        return self.call_with_circuit_breaker("PUT", endpoint, json=json, headers=headers)
    
    def delete(self, endpoint, headers=None):
        return self.call_with_circuit_breaker("DELETE", endpoint, headers=headers)


# Create API clients
dispatcher_client = APIClient("http://localhost:5001", "dispatcher")
tracking_client = APIClient("http://localhost:5002", "tracking")
notify_client = APIClient("http://localhost:5003", "notify")

def test_circuit_breaker():
    """Test circuit breaker by making failing requests"""
    import sys
    
    print("\n" + "="*60)
    print("Testing Circuit Breaker")
    print("="*60)
    
    # Make failing requests to trigger circuit breaker
    for i in range(5):
        try:
            print(f"\nAttempt {i+1}: Calling non-existent endpoint...")
            response = dispatcher_client.get("/non-existent-endpoint")
            print(f"Response: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")
            status = get_circuit_breaker_status()
            print(f"Circuit status: {status['dispatcher']['state']}")
            print(f"Failure count: {status['dispatcher']['failure_count']}")
        
        time.sleep(1)
    
    print("\n" + "="*60)
    print("Final Circuit Status:")
    print(json.dumps(get_circuit_breaker_status(), indent=2))

if __name__ == "__main__":
    test_circuit_breaker()
