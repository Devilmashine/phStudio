#!/usr/bin/env python3
"""
Script to run all performance tests
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, text=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    """Run all performance tests"""
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    print("Running Performance Test Suite")
    print("="*60)
    
    # 1. Run unit performance tests
    print("\n1. Running unit performance tests...")
    if not run_command([
        "pytest", 
        "tests/performance/test_api_performance.py", 
        "-v", 
        "--performance"
    ], "Unit Performance Tests"):
        print("Unit performance tests failed!")
        sys.exit(1)
    
    # 2. Run database performance tests
    print("\n2. Running database performance tests...")
    if not run_command([
        "pytest", 
        "tests/test_performance.py", 
        "-v", 
        "-m", "performance"
    ], "Database Performance Tests"):
        print("Database performance tests failed!")
        sys.exit(1)
    
    # 3. Run benchmark tests
    print("\n3. Running benchmark tests...")
    if not run_command([
        "python", 
        "tests/performance/benchmark.py", 
        "--scenario", "api_endpoints"
    ], "Benchmark Tests"):
        print("Benchmark tests failed!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("All performance tests completed successfully!")
    print("="*60)

if __name__ == "__main__":
    main()