#!/usr/bin/env python3
"""
Database connection health checker script.
Monitors PostgreSQL connection pool and performance metrics.
"""
import os
import sys
import time
import psutil
import psycopg2
from datetime import datetime
from psycopg2 import OperationalError
from urllib.parse import urlparse


def check_database_connection():
    """Check basic database connectivity."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Test connection
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Simple query to verify connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Check connection count
        cursor.execute("""
            SELECT count(*) as active_connections 
            FROM pg_stat_activity 
            WHERE state = 'active'
        """)
        active_connections = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection successful")
        print(f"📊 PostgreSQL Version: {version}")
        print(f"🔗 Active connections: {active_connections}")
        
        # Warn if too many connections
        if active_connections > 50:
            print(f"⚠️  High connection count: {active_connections}")
            return False
            
        return True
        
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_database_performance():
    """Check database performance metrics."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check database size
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
        """)
        db_size = cursor.fetchone()[0]
        print(f"💾 Database size: {db_size}")
        
        # Check slow queries
        cursor.execute("""
            SELECT count(*) as slow_queries 
            FROM pg_stat_activity 
            WHERE state = 'active' AND now() - query_start > interval '30 seconds'
        """)
        slow_queries = cursor.fetchone()[0]
        
        if slow_queries > 0:
            print(f"🐌 Slow queries detected: {slow_queries}")
        else:
            print("⚡ No slow queries detected")
        
        # Check locks
        cursor.execute("""
            SELECT count(*) as blocked_queries
            FROM pg_stat_activity 
            WHERE wait_event_type = 'Lock'
        """)
        blocked_queries = cursor.fetchone()[0]
        
        if blocked_queries > 0:
            print(f"🔒 Blocked queries: {blocked_queries}")
        else:
            print("🔓 No blocked queries")
        
        cursor.close()
        conn.close()
        
        return slow_queries == 0 and blocked_queries < 5
        
    except Exception as e:
        print(f"❌ Performance check failed: {e}")
        return False


def check_system_resources():
    """Check system resource usage."""
    try:
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        print(f"🧠 Memory usage: {memory_percent:.1f}%")
        print(f"💿 Disk usage: {disk_percent:.1f}%")
        print(f"⚙️  CPU usage: {cpu_percent:.1f}%")
        
        # Alert thresholds
        alerts = []
        if memory_percent > 85:
            alerts.append(f"High memory usage: {memory_percent:.1f}%")
        if disk_percent > 90:
            alerts.append(f"High disk usage: {disk_percent:.1f}%")
        if cpu_percent > 90:
            alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        if alerts:
            for alert in alerts:
                print(f"⚠️  {alert}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ System resource check failed: {e}")
        return False


def main():
    """Main health check function."""
    print(f"🔍 Starting database health check at {datetime.now()}")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 3
    
    # Database connectivity
    if check_database_connection():
        checks_passed += 1
    
    print("-" * 30)
    
    # Database performance  
    if check_database_performance():
        checks_passed += 1
        
    print("-" * 30)
    
    # System resources
    if check_system_resources():
        checks_passed += 1
    
    print("=" * 50)
    print(f"✅ Checks passed: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 All database health checks passed!")
        sys.exit(0)
    else:
        print("❌ Some health checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()