import time
import functools
import threading
from datetime import datetime
from logger_config import app_logger, api_logger

class CircuitBreaker:
    """Circuit Breaker pattern implementation"""
    
    def __init__(self, name, failure_threshold=3, recovery_timeout=30):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    api_logger.info(f"Circuit {self.name} transitioned from OPEN to HALF_OPEN")
                else:
                    api_logger.warning(f"Circuit {self.name} is OPEN, request rejected")
                    raise Exception(f"Circuit {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            with self.lock:
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    api_logger.info(f"Circuit {self.name} transitioned from HALF_OPEN to CLOSED")
            
            return result
            
        except Exception as e:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold and self.state != "OPEN":
                    self.state = "OPEN"
                    api_logger.error(f"Circuit {self.name} OPENED after {self.failure_count} failures")
            
            raise e
    
    def get_status(self):
        with self.lock:
            return {
                "name": self.name,
                "state": self.state,
                "failure_count": self.failure_count,
                "failure_threshold": self.failure_threshold
            }


def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    api_logger.info(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        api_logger.info(f"Success on attempt {attempt} for {func.__name__}")
                    return result
                except exceptions as e:
                    last_exception = e
                    api_logger.warning(f"Attempt {attempt} failed for {func.__name__}: {str(e)}")
                    
                    if attempt < max_attempts:
                        wait_time = current_delay
                        api_logger.info(f"Waiting {wait_time}s before next attempt")
                        time.sleep(wait_time)
                        current_delay *= backoff
                    else:
                        api_logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator


# Global circuit breakers
circuit_breakers = {
    "dispatcher": CircuitBreaker("dispatcher", failure_threshold=3, recovery_timeout=30),
    "tracking": CircuitBreaker("tracking", failure_threshold=3, recovery_timeout=30),
    "notify": CircuitBreaker("notify", failure_threshold=3, recovery_timeout=30)
}


def get_circuit_breaker_status():
    return {name: cb.get_status() for name, cb in circuit_breakers.items()}
