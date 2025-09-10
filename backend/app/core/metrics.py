"""
Application Metrics and Monitoring System
"""
import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from collections import defaultdict
from datetime import datetime, timezone
import asyncio

from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse

logger = logging.getLogger(__name__)

# Application metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

REQUEST_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

# Business metrics
BOOKING_COUNT = Counter(
    'bookings_total',
    'Total bookings created',
    ['status', 'source']
)

EMPLOYEE_LOGIN_COUNT = Counter(
    'employee_logins_total',
    'Total employee logins',
    ['role', 'status']
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total application errors',
    ['type', 'endpoint']
)

# Performance metrics
DATABASE_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

CACHE_HIT_RATE = Gauge(
    'cache_hit_rate',
    'Cache hit rate percentage'
)

# System metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Current memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'Current CPU usage percentage'
)

class MetricsCollector:
    """Central metrics collection and reporting"""
    
    def __init__(self):
        self.start_time = time.time()
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'error_count': 0
        })
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        
        # Update endpoint statistics
        stats = self.endpoint_stats[endpoint]
        stats['count'] += 1
        stats['total_duration'] += duration
        if status_code >= 400:
            stats['error_count'] += 1
    
    def record_booking(self, status: str, source: str):
        """Record booking creation metrics"""
        BOOKING_COUNT.labels(status=status, source=source).inc()
    
    def record_login(self, role: str, status: str):
        """Record employee login metrics"""
        EMPLOYEE_LOGIN_COUNT.labels(role=role, status=status).inc()
    
    def record_error(self, error_type: str, endpoint: str):
        """Record application error metrics"""
        ERROR_COUNT.labels(type=error_type, endpoint=endpoint).inc()
    
    def record_database_query(self, query_type: str, duration: float):
        """Record database query metrics"""
        DATABASE_QUERY_DURATION.labels(query_type=query_type).observe(duration)
    
    def update_cache_stats(self, hit_rate: float):
        """Update cache hit rate metrics"""
        CACHE_HIT_RATE.set(hit_rate)
    
    def update_system_metrics(self, memory_bytes: int, cpu_percent: float):
        """Update system resource metrics"""
        MEMORY_USAGE.set(memory_bytes)
        CPU_USAGE.set(cpu_percent)
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self.start_time
    
    def get_endpoint_stats(self) -> Dict[str, Any]:
        """Get detailed endpoint statistics"""
        stats = {}
        for endpoint, data in self.endpoint_stats.items():
            stats[endpoint] = {
                'count': data['count'],
                'average_duration': data['total_duration'] / data['count'] if data['count'] > 0 else 0,
                'error_rate': data['error_count'] / data['count'] if data['count'] > 0 else 0
            }
        return stats

# Global metrics collector instance
metrics_collector = MetricsCollector()

def metrics_middleware():
    """FastAPI middleware for collecting HTTP metrics"""
    def middleware(request: Request, call_next):
        async def wrapper():
            method = request.method
            endpoint = request.url.path
            
            # Record request in progress
            REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
            
            start_time = time.time()
            
            try:
                response = await call_next(request)
                duration = time.time() - start_time
                status_code = response.status_code
                
                # Record metrics
                metrics_collector.record_request(method, endpoint, status_code, duration)
                
                # Add metrics headers
                response.headers["X-Response-Time"] = str(duration)
                response.headers["X-Process-Time"] = str(duration)
                
                return response
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.record_request(method, endpoint, 500, duration)
                metrics_collector.record_error(type(e).__name__, endpoint)
                raise
            finally:
                # Decrement request in progress
                REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
        
        return wrapper()
    
    return middleware

def monitor_endpoint():
    """Decorator for monitoring specific endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint_name = func.__name__
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                REQUEST_DURATION.labels(method="FUNCTION", endpoint=endpoint_name).observe(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                ERROR_COUNT.labels(type=type(e).__name__, endpoint=endpoint_name).inc()
                REQUEST_DURATION.labels(method="FUNCTION", endpoint=endpoint_name).observe(duration)
                raise
        
        return wrapper
    return decorator

def record_database_query(query_type: str):
    """Decorator for monitoring database queries"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                metrics_collector.record_database_query(query_type, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.record_database_query(query_type, duration)
                raise
        
        return wrapper
    return decorator

# Prometheus metrics endpoint
async def metrics_endpoint(request: Request) -> Response:
    """Prometheus metrics endpoint"""
    try:
        # Update system metrics
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            metrics_collector.update_system_metrics(memory_info.rss, cpu_percent)
        except ImportError:
            logger.warning("psutil not installed, system metrics unavailable")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
        
        # Generate Prometheus metrics
        metrics_data = generate_latest()
        return PlainTextResponse(
            content=metrics_data.decode('utf-8'),
            headers={'Content-Type': CONTENT_TYPE_LATEST}
        )
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return PlainTextResponse(content="", status_code=500)

# Health check with metrics
def get_application_health() -> Dict[str, Any]:
    """Get comprehensive application health with metrics"""
    uptime = metrics_collector.get_uptime()
    endpoint_stats = metrics_collector.get_endpoint_stats()
    
    # Calculate overall health score
    total_requests = sum(stats['count'] for stats in endpoint_stats.values())
    total_errors = sum(stats['error_count'] for stats in endpoint_stats.values())
    error_rate = total_errors / total_requests if total_requests > 0 else 0
    
    health_score = 100 - (error_rate * 100)
    
    return {
        "status": "healthy" if health_score > 95 else "degraded" if health_score > 80 else "unhealthy",
        "uptime_seconds": round(uptime, 2),
        "health_score": round(health_score, 2),
        "metrics": {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 4),
            "endpoint_stats": endpoint_stats
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }