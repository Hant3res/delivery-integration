import json
import time
from functools import wraps
from logger_config import app_logger

class SimpleCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key):
        """Get value from cache if not expired"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if expiry > time.time():
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key, value, ttl_seconds=300):
        """Set value in cache with TTL"""
        expiry = time.time() + ttl_seconds
        self._cache[key] = (value, expiry)
    
    def delete(self, key):
        """Delete from cache"""
        self._cache.pop(key, None)
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
    
    def cached(self, ttl_seconds=300, key_prefix=None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = key_prefix or f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    app_logger.debug(f"Cache HIT for {cache_key}")
                    return cached_result
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, result, ttl_seconds)
                app_logger.debug(f"Cache MISS for {cache_key}, stored")
                
                return result
            return wrapper
        return decorator

# Global cache instance
cache = SimpleCache()
