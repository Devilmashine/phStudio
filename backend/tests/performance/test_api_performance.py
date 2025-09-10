"""
API Performance Testing Framework
Comprehensive performance tests for all API endpoints
"""

import pytest
import time
import asyncio
import statistics
from typing import List, Dict
import json
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Performance thresholds (in seconds)
PERFORMANCE_THRESHOLDS = {
    "GET /api/bookings/": 0.5,
    "GET /api/bookings/{id}": 0.3,
    "POST /api/bookings/": 0.8,
    "GET /api/calendar/": 0.4,
    "GET /api/gallery/": 0.3,
    "GET /api/news/": 0.3,
    "GET /api/users/": 0.5,
    "GET /api/health": 0.1,
    "GET /api/monitoring/metrics": 0.2
}

class PerformanceMetrics:
    """Collect and analyze performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
    
    def record_time(self, endpoint: str, duration: float):
        """Record execution time for an endpoint"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
        self.metrics[endpoint].append(duration)
    
    def get_stats(self, endpoint: str) -> Dict[str, float]:
        """Get performance statistics for an endpoint"""
        if endpoint not in self.metrics or not self.metrics[endpoint]:
            return {}
        
        times = self.metrics[endpoint]
        return {
            "count": len(times),
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "p95": self.percentile(times, 95),
            "p99": self.percentile(times, 99)
        }
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def check_thresholds(self) -> List[Dict[str, any]]:
        """Check if all endpoints meet performance thresholds"""
        violations = []
        for endpoint, times in self.metrics.items():
            if endpoint in PERFORMANCE_THRESHOLDS:
                avg_time = statistics.mean(times)
                threshold = PERFORMANCE_THRESHOLDS[endpoint]
                if avg_time > threshold:
                    violations.append({
                        "endpoint": endpoint,
                        "avg_time": avg_time,
                        "threshold": threshold,
                        "violation": avg_time - threshold
                    })
        return violations

# Global metrics collector
metrics_collector = PerformanceMetrics()

def time_it(func):
    """Decorator to time function execution"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        
        # Record metrics (assuming first arg is endpoint name for API calls)
        if args and isinstance(args[0], str):
            metrics_collector.record_time(args[0], duration)
        
        return result, duration
    return wrapper

@pytest.mark.performance
@pytest.mark.integration
class TestAPIPerformance:
    """Performance tests for API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient, db_session: Session):
        """Setup test data"""
        self.client = client
        self.db_session = db_session
        
        # Create test data
        self._create_test_bookings(50)
        self._create_test_users(20)
        self._create_test_gallery_images(30)
        self._create_test_news(10)
    
    def _create_test_bookings(self, count: int):
        """Create test bookings"""
        from datetime import datetime, timezone
        
        for i in range(count):
            future_date = datetime.now(timezone.utc) + timedelta(days=i % 30)
            start_time = future_date.replace(hour=10 + (i % 8), minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=2)
            
            booking_data = {
                "date": future_date.date().isoformat(),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_price": 1000.0 + (i * 50),
                "client_name": f"Client {i}",
                "client_phone": f"+7900123456{i:02d}"
            }
            
            # Note: In real tests, you would create bookings via the API or directly in DB
    
    def _create_test_users(self, count: int):
        """Create test users"""
        # Implementation would depend on user model
        pass
    
    def _create_test_gallery_images(self, count: int):
        """Create test gallery images"""
        # Implementation would depend on gallery model
        pass
    
    def _create_test_news(self, count: int):
        """Create test news articles"""
        # Implementation would depend on news model
        pass
    
    @time_it
    def test_bookings_list_performance(self, endpoint="/api/bookings/"):
        """Test performance of bookings list endpoint"""
        response = self.client.get(endpoint)
        assert response.status_code == 200
        return response
    
    @time_it
    def test_single_booking_performance(self, endpoint="/api/bookings/1"):
        """Test performance of single booking endpoint"""
        response = self.client.get(endpoint)
        # 404 is expected if booking doesn't exist
        assert response.status_code in [200, 404]
        return response
    
    @time_it
    def test_calendar_performance(self, endpoint="/api/calendar/"):
        """Test performance of calendar endpoint"""
        response = self.client.get(endpoint)
        assert response.status_code == 200
        return response
    
    @time_it
    def test_gallery_performance(self, endpoint="/api/gallery/"):
        """Test performance of gallery endpoint"""
        response = self.client.get(endpoint)
        assert response.status_code == 200
        return response
    
    @time_it
    def test_news_performance(self, endpoint="/api/news/"):
        """Test performance of news endpoint"""
        response = self.client.get(endpoint)
        assert response.status_code == 200
        return response
    
    @time_it
    def test_health_endpoint_performance(self, endpoint="/api/health"):
        """Test performance of health endpoint"""
        response = self.client.get(endpoint)
        assert response.status_code == 200
        return response
    
    @time_it
    def test_metrics_endpoint_performance(self, endpoint="/api/monitoring/metrics"):
        """Test performance of metrics endpoint"""
        response = self.client.get(endpoint)
        # Metrics endpoint might return 404 if not implemented
        assert response.status_code in [200, 404]
        return response
    
    def test_concurrent_requests_performance(self):
        """Test performance under concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            return self.client.get("/api/bookings/")
        
        # Test with 10 concurrent requests
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Total time should be reasonable
        assert total_time < 3.0  # 10 requests should complete in < 3 seconds
        
        print(f"10 concurrent requests completed in {total_time:.3f} seconds")
    
    def test_response_size_performance(self):
        """Test API response sizes"""
        endpoints = [
            "/api/bookings/",
            "/api/calendar/",
            "/api/gallery/",
            "/api/news/"
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code == 200
            
            # Response size should be reasonable
            response_size = len(response.content)
            assert response_size < 1024 * 1024  # Less than 1MB
            
            print(f"{endpoint}: {response_size} bytes")
    
    @pytest.mark.slow
    def test_load_performance(self):
        """Test performance under sustained load"""
        # Make 100 requests and measure performance
        times = []
        
        for i in range(100):
            start_time = time.time()
            response = self.client.get("/api/bookings/")
            end_time = time.time()
            
            assert response.status_code == 200
            times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        p95_time = metrics_collector.percentile(times, 95)
        p99_time = metrics_collector.percentile(times, 99)
        
        print(f"Load test results (100 requests):")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Median: {median_time:.3f}s")
        print(f"  95th percentile: {p95_time:.3f}s")
        print(f"  99th percentile: {p99_time:.3f}s")
        
        # Performance should remain consistent
        assert avg_time < 0.6  # Average should be < 600ms
        assert p95_time < 1.0  # 95% should be < 1s
        assert p99_time < 1.5  # 99% should be < 1.5s

@pytest.mark.performance
@pytest.mark.database
class TestDatabasePerformance:
    """Database performance tests"""
    
    def test_query_performance(self, db_session: Session):
        """Test database query performance"""
        # This would test specific database queries
        pass
    
    def test_connection_pool_performance(self, db_session: Session):
        """Test database connection pool performance"""
        # This would test connection pool behavior
        pass

# Performance report generation
def generate_performance_report():
    """Generate a performance test report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {},
        "threshold_violations": [],
        "summary": {}
    }
    
    # Collect metrics
    for endpoint in metrics_collector.metrics:
        report["metrics"][endpoint] = metrics_collector.get_stats(endpoint)
    
    # Check thresholds
    violations = metrics_collector.check_thresholds()
    report["threshold_violations"] = violations
    
    # Generate summary
    total_endpoints = len(metrics_collector.metrics)
    violating_endpoints = len(violations)
    
    report["summary"] = {
        "total_endpoints_tested": total_endpoints,
        "endpoints_meeting_thresholds": total_endpoints - violating_endpoints,
        "endpoints_violating_thresholds": violating_endpoints,
        "performance_score": ((total_endpoints - violating_endpoints) / total_endpoints * 100) if total_endpoints > 0 else 100
    }
    
    return report

# Pytest hooks for performance reporting
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generate performance report at the end of tests"""
    if hasattr(config, 'workerinput'):  # Skip in xdist workers
        return
    
    # Only generate report if performance tests were run
    if metrics_collector.metrics:
        report = generate_performance_report()
        
        terminalreporter.section("Performance Test Report", sep="-", bold=True)
        terminalreporter.write_line(f"Performance Score: {report['summary']['performance_score']:.1f}%")
        terminalreporter.write_line(f"Endpoints Meeting Thresholds: {report['summary']['endpoints_meeting_thresholds']}/{report['summary']['total_endpoints_tested']}")
        
        if report["threshold_violations"]:
            terminalreporter.write_line("\nThreshold Violations:")
            for violation in report["threshold_violations"]:
                terminalreporter.write_line(f"  {violation['endpoint']}: {violation['avg_time']:.3f}s > {violation['threshold']:.3f}s")
        
        # Save detailed report to file
        with open("performance_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        terminalreporter.write_line(f"\nDetailed report saved to performance_report.json")