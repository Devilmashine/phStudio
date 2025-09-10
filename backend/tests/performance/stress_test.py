"""
Stress Testing Framework
High-load testing to identify system breaking points
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StressTestRunner:
    """Run stress tests on the API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "test_runs": [],
            "aggregated_metrics": {}
        }
    
    async def run_stress_test(self, 
                             endpoint: str, 
                             concurrent_users: int, 
                             requests_per_user: int,
                             ramp_up_time: int = 30) -> Dict:
        """Run a stress test on a specific endpoint"""
        
        logger.info(f"Starting stress test: {concurrent_users} users, {requests_per_user} requests each")
        
        # Track test start
        test_start_time = time.time()
        
        # Create tasks for all users
        tasks = []
        for user_id in range(concurrent_users):
            task = self._run_user_session(user_id, endpoint, requests_per_user, ramp_up_time)
            tasks.append(task)
        
        # Run all user sessions concurrently
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate test duration
        test_duration = time.time() - test_start_time
        
        # Process results
        successful_requests = 0
        failed_requests = 0
        response_times = []
        errors = []
        
        for result in user_results:
            if isinstance(result, Exception):
                errors.append(str(result))
                continue
            
            successful_requests += result["successful_requests"]
            failed_requests += result["failed_requests"]
            response_times.extend(result["response_times"])
        
        # Calculate metrics
        total_requests = successful_requests + failed_requests
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        metrics = {
            "test_parameters": {
                "endpoint": endpoint,
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user,
                "ramp_up_time": ramp_up_time,
                "total_requests": total_requests
            },
            "results": {
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": success_rate,
                "test_duration_seconds": test_duration,
                "requests_per_second": total_requests / test_duration if test_duration > 0 else 0
            },
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "average": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": self._percentile(response_times, 95) if response_times else 0,
                "p99": self._percentile(response_times, 99) if response_times else 0
            },
            "errors": errors
        }
        
        # Store results
        self.results["test_runs"].append(metrics)
        
        logger.info(f"Stress test completed: {success_rate:.1f}% success rate")
        return metrics
    
    async def _run_user_session(self, 
                               user_id: int, 
                               endpoint: str, 
                               requests_count: int, 
                               ramp_up_time: int) -> Dict:
        """Run a single user session"""
        # Stagger user start times
        delay = (user_id / ramp_up_time) if ramp_up_time > 0 else 0
        await asyncio.sleep(delay)
        
        successful_requests = 0
        failed_requests = 0
        response_times = []
        errors = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(requests_count):
                try:
                    start_time = time.time()
                    
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        await response.read()  # Read response body
                        
                        end_time = time.time()
                        response_time = end_time - start_time
                        response_times.append(response_time)
                        
                        if response.status == 200:
                            successful_requests += 1
                        else:
                            failed_requests += 1
                            errors.append(f"HTTP {response.status}")
                            
                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
                
                # Small delay between requests to simulate realistic usage
                await asyncio.sleep(0.01)
        
        return {
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "response_times": response_times,
            "errors": errors
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def run_progressive_load_test(self, 
                                 endpoint: str,
                                 max_users: int = 100,
                                 step_size: int = 10,
                                 requests_per_user: int = 10) -> List[Dict]:
        """Run progressive load test, gradually increasing load"""
        
        results = []
        
        for user_count in range(step_size, max_users + 1, step_size):
            logger.info(f"Running test with {user_count} concurrent users")
            
            # Run stress test
            result = asyncio.run(self.run_stress_test(
                endpoint=endpoint,
                concurrent_users=user_count,
                requests_per_user=requests_per_user
            ))
            
            results.append(result)
            
            # Check if we should stop (if error rate is too high)
            if result["results"]["success_rate"] < 90:
                logger.warning(f"High error rate ({result['results']['success_rate']:.1f}%), stopping test")
                break
            
            # Wait between tests to allow system to recover
            time.sleep(5)
        
        return results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive stress test report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "test_runs": self.results["test_runs"],
            "summary": self._generate_summary()
        }
        
        return report
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        if not self.results["test_runs"]:
            return {}
        
        # Find breaking point (where success rate drops below 95%)
        breaking_point = None
        max_throughput = 0
        max_throughput_run = None
        
        for run in self.results["test_runs"]:
            success_rate = run["results"]["success_rate"]
            throughput = run["results"]["requests_per_second"]
            
            # Track breaking point
            if success_rate < 95 and breaking_point is None:
                breaking_point = run["test_parameters"]["concurrent_users"]
            
            # Track maximum throughput
            if throughput > max_throughput:
                max_throughput = throughput
                max_throughput_run = run
        
        return {
            "total_test_runs": len(self.results["test_runs"]),
            "breaking_point_users": breaking_point,
            "max_throughput_rps": max_throughput,
            "max_throughput_config": max_throughput_run["test_parameters"] if max_throughput_run else None
        }

# Predefined stress test scenarios
STRESS_TEST_SCENARIOS = {
    "basic_load": {
        "name": "Basic Load Test",
        "description": "Test basic API endpoints under moderate load",
        "tests": [
            {"endpoint": "/api/health", "users": 50, "requests_per_user": 20},
            {"endpoint": "/api/bookings/", "users": 30, "requests_per_user": 15},
            {"endpoint": "/api/calendar/", "users": 25, "requests_per_user": 10}
        ]
    },
    "high_load": {
        "name": "High Load Test",
        "description": "Test API under high concurrent load",
        "tests": [
            {"endpoint": "/api/bookings/", "users": 100, "requests_per_user": 25},
            {"endpoint": "/api/health", "users": 200, "requests_per_user": 50}
        ]
    },
    "progressive_load": {
        "name": "Progressive Load Test",
        "description": "Gradually increase load to find breaking point",
        "tests": [
            {"endpoint": "/api/bookings/", "max_users": 150, "step_size": 15, "requests_per_user": 10}
        ]
    }
}

async def run_scenario(runner: StressTestRunner, scenario_name: str) -> List[Dict]:
    """Run a predefined stress test scenario"""
    if scenario_name not in STRESS_TEST_SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    
    scenario = STRESS_TEST_SCENARIOS[scenario_name]
    logger.info(f"Running scenario: {scenario['name']}")
    
    results = []
    
    for test_config in scenario["tests"]:
        if "max_users" in test_config:
            # Progressive load test
            test_results = runner.run_progressive_load_test(
                endpoint=test_config["endpoint"],
                max_users=test_config["max_users"],
                step_size=test_config["step_size"],
                requests_per_user=test_config["requests_per_user"]
            )
            results.extend(test_results)
        else:
            # Standard stress test
            result = await runner.run_stress_test(
                endpoint=test_config["endpoint"],
                concurrent_users=test_config["users"],
                requests_per_user=test_config["requests_per_user"]
            )
            results.append(result)
    
    return results

# Command line interface
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Stress test the Photo Studio API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--scenario", choices=STRESS_TEST_SCENARIOS.keys(), 
                       default="basic_load", help="Test scenario to run")
    parser.add_argument("--endpoint", help="Specific endpoint to test")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--requests", type=int, default=10, help="Requests per user")
    parser.add_argument("--output", default="stress_test_report.json", help="Output file for results")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = StressTestRunner(base_url=args.url)
    
    try:
        if args.endpoint:
            # Run single endpoint test
            logger.info(f"Testing endpoint: {args.endpoint}")
            result = asyncio.run(runner.run_stress_test(
                endpoint=args.endpoint,
                concurrent_users=args.users,
                requests_per_user=args.requests
            ))
            
            # Generate and save report
            report = runner.generate_report()
            
        else:
            # Run predefined scenario
            logger.info(f"Running scenario: {args.scenario}")
            asyncio.run(run_scenario(runner, args.scenario))
            
            # Generate and save report
            report = runner.generate_report()
        
        # Save report
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Stress test report saved to {args.output}")
        
        # Print summary
        summary = report["summary"]
        print(f"\n--- Stress Test Summary ---")
        print(f"Total test runs: {summary['total_test_runs']}")
        print(f"Breaking point: {summary['breaking_point_users']} users")
        print(f"Maximum throughput: {summary['max_throughput_rps']:.2f} requests/second")
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)