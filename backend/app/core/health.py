"""
Database Health Check and Monitoring Utilities for PostgreSQL
"""
import logging
import time
from typing import Dict, Any, Optional
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from ..core.database import get_engine, get_db
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class DatabaseHealth:
    """Database health monitoring and diagnostics"""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = get_engine()
    
    def check_connection(self) -> Dict[str, Any]:
        """Check basic database connectivity"""
        try:
            start_time = time.time()
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as health_check"))
                result.fetchone()
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database_url": self._mask_db_url(str(self.engine.url))
            }
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def check_tables(self) -> Dict[str, Any]:
        """Check if all required tables exist and are accessible"""
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                "users", "bookings", "clients", "calendar_events", 
                "gallery_images", "news", "studio_settings"
            ]
            
            missing_tables = [table for table in required_tables if table not in tables]
            
            return {
                "status": "healthy" if not missing_tables else "warning",
                "existing_tables": tables,
                "missing_tables": missing_tables,
                "total_tables": len(tables),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Table check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def check_connection_pool(self) -> Dict[str, Any]:
        """Check connection pool status"""
        try:
            pool = self.engine.pool
            
            return {
                "status": "healthy",
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Connection pool check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def check_performance(self) -> Dict[str, Any]:
        """Check database performance metrics"""
        try:
            queries = [
                # Basic SELECT performance
                ("SELECT COUNT(*) FROM users", "users_count"),
                ("SELECT COUNT(*) FROM bookings", "bookings_count"),
                ("SELECT COUNT(*) FROM calendar_events", "events_count"),
            ]
            
            results = {}
            for query, name in queries:
                start_time = time.time()
                with self.engine.connect() as conn:
                    result = conn.execute(text(query))
                    count = result.scalar()
                
                response_time = time.time() - start_time
                results[name] = {
                    "count": count,
                    "response_time_ms": round(response_time * 1000, 2)
                }
            
            return {
                "status": "healthy",
                "metrics": results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Performance check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def full_health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        start_time = time.time()
        
        checks = {
            "connection": self.check_connection(),
            "tables": self.check_tables(),
            "connection_pool": self.check_connection_pool(),
            "performance": self.check_performance()
        }
        
        # Determine overall status
        statuses = [check.get("status") for check in checks.values()]
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        total_time = time.time() - start_time
        
        return {
            "overall_status": overall_status,
            "total_check_time_ms": round(total_time * 1000, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": self.settings.ENV,
            "checks": checks
        }
    
    def _mask_db_url(self, url: str) -> str:
        """Mask sensitive information in database URL"""
        if "postgresql://" in url:
            # Replace password with asterisks
            parts = url.split(":")
            if len(parts) >= 3:
                # postgresql://user:password@host:port/db
                user_pass = parts[2].split("@")[0]
                masked = "*" * len(user_pass)
                return url.replace(user_pass, masked)
        return url

# Singleton instance
db_health = DatabaseHealth()

async def get_database_health() -> Dict[str, Any]:
    """FastAPI dependency for database health checks"""
    return db_health.full_health_check()

def log_health_metrics():
    """Log health metrics for monitoring systems"""
    health = db_health.full_health_check()
    
    if health["overall_status"] == "healthy":
        logger.info(f"Database health check passed in {health['total_check_time_ms']}ms")
    else:
        logger.warning(f"Database health check issues detected: {health['overall_status']}")
        
    return health