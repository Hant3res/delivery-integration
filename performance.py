import time
import functools
import asyncio
import threading
from datetime import datetime
from logger_config import app_logger

class PerformanceMonitor:
    """Performance monitoring and benchmarking"""
    
    def __init__(self):
        self.metrics = {}
    
    def measure_time(self, name=None):
        """Decorator to measure function execution time"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()
                duration = (end - start) * 1000  # milliseconds
                
                metric_name = name or func.__name__
                if metric_name not in self.metrics:
                    self.metrics[metric_name] = []
                self.metrics[metric_name].append(duration)
                
                app_logger.info(f"⏱ {metric_name} took {duration:.2f}ms")
                return result
            return wrapper
        return decorator
    
    def measure_async(self, name=None):
        """Decorator for async functions"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = await func(*args, **kwargs)
                end = time.perf_counter()
                duration = (end - start) * 1000
                
                metric_name = name or func.__name__
                if metric_name not in self.metrics:
                    self.metrics[metric_name] = []
                self.metrics[metric_name].append(duration)
                
                app_logger.info(f"⏱ {metric_name} took {duration:.2f}ms")
                return result
            return wrapper
        return decorator
    
    def get_statistics(self):
        """Get performance statistics"""
        stats = {}
        for name, times in self.metrics.items():
            if times:
                stats[name] = {
                    "count": len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "avg_ms": sum(times) / len(times),
                    "total_ms": sum(times)
                }
        return stats
    
    def reset(self):
        self.metrics = {}

# Global performance monitor
perf_monitor = PerformanceMonitor()

class Benchmark:
    """Benchmark utility for comparing before/after"""
    
    @staticmethod
    def run_benchmark(name, func, iterations=10):
        """Run benchmark multiple times and return statistics"""
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        return {
            "name": name,
            "iterations": iterations,
            "min_ms": min(times),
            "max_ms": max(times),
            "avg_ms": sum(times) / len(times)
        }
    
    @staticmethod
    def compare(before_result, after_result):
        """Compare before and after benchmark results"""
        before_avg = before_result["avg_ms"]
        after_avg = after_result["avg_ms"]
        
        if before_avg > 0:
            improvement = (before_avg - after_avg) / before_avg * 100
        else:
            improvement = 0
        
        return {
            "before_ms": before_avg,
            "after_ms": after_avg,
            "improvement_percent": improvement,
            "speedup_factor": before_avg / after_avg if after_avg > 0 else 0
        }
