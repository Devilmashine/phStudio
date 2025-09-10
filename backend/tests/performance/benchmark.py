"""
Performance Benchmarking Framework
Compare performance before and after changes
"""

import time
import statistics
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Callable, Any
import subprocess
import os

class PerformanceBenchmark:
    """Run performance benchmarks and compare results"""
    
    def __init__(self, baseline_file: str = "performance_baseline.json"):
        self.baseline_file = baseline_file
        self.current_results = {}
        self.baseline_results = self._load_baseline()
    
    def _load_baseline(self) -> Dict:
        """Load baseline performance results"""
        if os.path.exists(self.baseline_file):
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        return {}
    
    def benchmark_function(self, 
                          name: str, 
                          func: Callable, 
                          *args, 
                          iterations: int = 100,
                          warmup: int = 10) -> Dict[str, Any]:
        """Benchmark a function"""
        # Warmup runs
        for _ in range(warmup):
            func(*args)
        
        # Actual benchmark runs
        times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            result = func(*args)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        # Calculate statistics
        stats = {
            "name": name,
            "iterations": iterations,
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "p95": self._percentile(times, 95),
            "p99": self._percentile(times, 99)
        }
        
        self.current_results[name] = stats
        return stats
    
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
    
    def benchmark_api_endpoint(self, 
                              name: str,
                              url: str,
                              method: str = "GET",
                              headers: Dict = None,
                              data: Dict = None,
                              iterations: int = 50) -> Dict[str, Any]:
        """Benchmark an API endpoint using curl"""
        import subprocess
        import json
        
        times = []
        
        for i in range(iterations):
            # Build curl command
            cmd = ["curl", "-s", "-w", "%{time_total}", "-o", "/dev/null"]
            
            if headers:
                for key, value in headers.items():
                    cmd.extend(["-H", f"{key}: {value}"])
            
            if method != "GET":
                cmd.extend(["-X", method])
            
            if data:
                cmd.extend(["-d", json.dumps(data)])
            
            cmd.append(url)
            
            # Execute request and measure time
            try:
                start_time = time.perf_counter()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                end_time = time.perf_counter()
                
                # Extract time from curl output
                if result.returncode == 0 and result.stdout:
                    # The time is the last part of the output
                    try:
                        curl_time = float(result.stdout.strip())
                        times.append(curl_time)
                    except ValueError:
                        # Fallback to perf_counter time
                        times.append(end_time - start_time)
            except subprocess.TimeoutExpired:
                print(f"Request {i+1} timed out")
            except Exception as e:
                print(f"Error in request {i+1}: {e}")
        
        if not times:
            return {"name": name, "error": "No successful requests"}
        
        # Calculate statistics
        stats = {
            "name": name,
            "iterations": len(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "p95": self._percentile(times, 95),
            "p99": self._percentile(times, 99)
        }
        
        self.current_results[name] = stats
        return stats
    
    def compare_with_baseline(self) -> Dict[str, Any]:
        """Compare current results with baseline"""
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "comparisons": []
        }
        
        for name, current_stats in self.current_results.items():
            if name in self.baseline_results:
                baseline_stats = self.baseline_results[name]
                
                # Calculate improvements/regressions
                mean_improvement = ((baseline_stats["mean"] - current_stats["mean"]) / baseline_stats["mean"]) * 100
                median_improvement = ((baseline_stats["median"] - current_stats["median"]) / baseline_stats["median"]) * 100
                
                comparison["comparisons"].append({
                    "name": name,
                    "current": current_stats,
                    "baseline": baseline_stats,
                    "improvement": {
                        "mean": mean_improvement,
                        "median": median_improvement
                    },
                    "status": "improved" if mean_improvement > 5 else "regressed" if mean_improvement < -5 else "similar"
                })
            else:
                comparison["comparisons"].append({
                    "name": name,
                    "current": current_stats,
                    "baseline": None,
                    "status": "new"
                })
        
        return comparison
    
    def save_baseline(self):
        """Save current results as baseline"""
        with open(self.baseline_file, 'w') as f:
            json.dump(self.current_results, f, indent=2)
        print(f"Baseline saved to {self.baseline_file}")
    
    def save_results(self, filename: str = None):
        """Save current results to file"""
        if filename is None:
            filename = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "results": self.current_results
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")
    
    def print_report(self, comparison: Dict = None):
        """Print a formatted performance report"""
        if comparison is None:
            comparison = {"comparisons": [{"name": name, "current": stats} 
                                        for name, stats in self.current_results.items()]}
        
        print("\n" + "="*80)
        print("PERFORMANCE BENCHMARK REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for comp in comparison["comparisons"]:
            name = comp["name"]
            current = comp["current"]
            
            print(f"{name}:")
            print(f"  Mean Time: {current['mean']:.6f}s")
            print(f"  Median Time: {current['median']:.6f}s")
            print(f"  Min/Max: {current['min']:.6f}s / {current['max']:.6f}s")
            print(f"  Std Dev: {current['std_dev']:.6f}s")
            
            if "baseline" in comp and comp["baseline"]:
                baseline = comp["baseline"]
                improvement = comp["improvement"]
                status = comp["status"]
                
                print(f"  Baseline Mean: {baseline['mean']:.6f}s")
                print(f"  Improvement: {improvement['mean']:+.2f}% (mean)")
                print(f"  Status: {status.upper()}")
            
            print()

# Common benchmark scenarios
BENCHMARK_SCENARIOS = {
    "database_queries": {
        "name": "Database Query Performance",
        "description": "Benchmark common database queries",
        "benchmarks": [
            # These would be actual database query functions
        ]
    },
    "api_endpoints": {
        "name": "API Endpoint Performance",
        "description": "Benchmark key API endpoints",
        "benchmarks": [
            {
                "name": "Health Check",
                "url": "http://localhost:8000/api/health",
                "method": "GET"
            },
            {
                "name": "Bookings List",
                "url": "http://localhost:8000/api/bookings/",
                "method": "GET"
            },
            {
                "name": "Calendar View",
                "url": "http://localhost:8000/api/calendar/",
                "method": "GET"
            }
        ]
    }
}

def run_benchmark_scenario(benchmark: PerformanceBenchmark, scenario_name: str):
    """Run a predefined benchmark scenario"""
    if scenario_name not in BENCHMARK_SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    
    scenario = BENCHMARK_SCENARIOS[scenario_name]
    print(f"Running benchmark scenario: {scenario['name']}")
    
    if scenario_name == "api_endpoints":
        for benchmark_config in scenario["benchmarks"]:
            benchmark.benchmark_api_endpoint(
                name=benchmark_config["name"],
                url=benchmark_config["url"],
                method=benchmark_config["method"],
                iterations=20
            )

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance benchmarking tool")
    parser.add_argument("--scenario", choices=BENCHMARK_SCENARIOS.keys(), 
                       default="api_endpoints", help="Benchmark scenario to run")
    parser.add_argument("--baseline", action="store_true", 
                       help="Save results as new baseline")
    parser.add_argument("--compare", action="store_true", 
                       help="Compare with existing baseline")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Create benchmark instance
    benchmark = PerformanceBenchmark()
    
    try:
        # Run benchmark scenario
        run_benchmark_scenario(benchmark, args.scenario)
        
        # Generate comparison if requested
        if args.compare and benchmark.baseline_results:
            comparison = benchmark.compare_with_baseline()
            
            # Print report
            benchmark.print_report(comparison)
            
            # Save comparison
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(comparison, f, indent=2)
                print(f"Comparison saved to {args.output}")
        else:
            # Print current results
            benchmark.print_report()
            
            # Save results
            if args.output:
                benchmark.save_results(args.output)
        
        # Save as baseline if requested
        if args.baseline:
            benchmark.save_baseline()
            
    except Exception as e:
        print(f"Error running benchmark: {e}")
        exit(1)