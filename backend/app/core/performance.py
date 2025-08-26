"""
PostgreSQL Performance Optimization Utilities
Contains database-specific optimizations and query enhancements
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from contextlib import contextmanager
import time
from functools import wraps

from .database import get_engine, get_db
from .config import get_settings

logger = logging.getLogger(__name__)

class PostgreSQLOptimizer:
    """PostgreSQL-specific performance optimizations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = get_engine()
    
    def setup_connection_events(self):
        """Setup SQLAlchemy events for PostgreSQL optimization"""
        
        @event.listens_for(self.engine, "connect")
        def set_postgresql_options(dbapi_connection, connection_record):
            """Set PostgreSQL-specific connection options"""
            with dbapi_connection.cursor() as cursor:
                # Set timezone to UTC
                cursor.execute("SET timezone TO 'UTC'")
                
                # Optimize for read-heavy workloads
                cursor.execute("SET default_statistics_target TO 100")
                
                # Enable query planning optimizations
                cursor.execute("SET enable_seqscan TO on")
                cursor.execute("SET enable_indexscan TO on")
                cursor.execute("SET enable_bitmapscan TO on")
                
                # Set work memory for complex queries
                cursor.execute("SET work_mem TO '4MB'")
                
                # Enable statement timeout (5 minutes)
                cursor.execute("SET statement_timeout TO '300s'")
                
                # Log slow queries in development
                if self.settings.ENV == "development":
                    cursor.execute("SET log_min_duration_statement TO 1000")
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def log_slow_queries(conn, cursor, statement, parameters, context, executemany):
            """Log query execution time"""
            context._query_start_time = time.time()
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def log_query_performance(conn, cursor, statement, parameters, context, executemany):
            """Log slow queries for optimization"""
            total = time.time() - context._query_start_time
            
            # Log queries slower than 1 second
            if total > 1.0:
                logger.warning(f"Slow query ({total:.2f}s): {statement[:200]}...")
    
    def create_indexes(self, db: Session) -> bool:
        """Create performance-critical indexes"""
        try:
            indexes = [
                # Booking optimization indexes
                "CREATE INDEX IF NOT EXISTS idx_bookings_date_status ON bookings(date, status)",
                "CREATE INDEX IF NOT EXISTS idx_bookings_client_phone_partial ON bookings(client_phone) WHERE status != 'cancelled'",
                
                # Calendar event indexes
                "CREATE INDEX IF NOT EXISTS idx_calendar_events_time_range ON calendar_events USING btree (start_time, end_time)",
                "CREATE INDEX IF NOT EXISTS idx_calendar_events_status_date ON calendar_events(status, start_time)",
                
                # User indexes
                "CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role) WHERE is_active = 'true'",
                
                # News indexes
                "CREATE INDEX IF NOT EXISTS idx_news_published_created ON news(published, created_at DESC)",
                
                # Gallery indexes
                "CREATE INDEX IF NOT EXISTS idx_gallery_category_featured ON gallery_images(category, is_featured)",
            ]
            
            for index_sql in indexes:
                db.execute(text(index_sql))
            
            db.commit()
            logger.info("Performance indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            db.rollback()
            return False
    
    def analyze_query_performance(self, db: Session, query: str) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN ANALYZE"""
        try:
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = db.execute(text(explain_query)).fetchone()
            
            if result:
                return result[0][0]  # JSON result
            
            return {}
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return {}
    
    def optimize_table(self, db: Session, table_name: str) -> bool:
        """Optimize specific table"""
        try:
            # Update table statistics
            db.execute(text(f"ANALYZE {table_name}"))
            
            # Vacuum if needed (non-blocking)
            db.execute(text(f"VACUUM {table_name}"))
            
            db.commit()
            logger.info(f"Table {table_name} optimized")
            return True
            
        except Exception as e:
            logger.error(f"Table optimization failed for {table_name}: {e}")
            db.rollback()
            return False

# Performance monitoring decorator
def monitor_query_performance(func):
    """Decorator to monitor database query performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 0.5:  # Log queries slower than 500ms
                logger.warning(f"Slow function {func.__name__}: {execution_time:.3f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

@contextmanager
def optimized_db_session():
    """Context manager for optimized database sessions"""
    db = next(get_db())
    try:
        # Set session-specific optimizations
        db.execute(text("SET LOCAL enable_seqscan TO off WHERE cost > 10000"))
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Connection pool monitoring
class ConnectionPoolMonitor:
    """Monitor and optimize connection pool usage"""
    
    def __init__(self):
        self.engine = get_engine()
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current connection pool status"""
        pool = self.engine.pool
        
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
            "utilization": pool.checkedout() / (pool.size() + pool.overflow()) * 100
        }
    
    def log_pool_stats(self):
        """Log connection pool statistics"""
        stats = self.get_pool_status()
        
        if stats["utilization"] > 80:
            logger.warning(f"High connection pool utilization: {stats['utilization']:.1f}%")
        
        logger.info(f"Pool stats: {stats['checked_out']}/{stats['size']} connections in use")

# Singleton instances
postgresql_optimizer = PostgreSQLOptimizer()
pool_monitor = ConnectionPoolMonitor()

# Initialize optimizations
def initialize_optimizations():
    """Initialize all PostgreSQL optimizations"""
    try:
        postgresql_optimizer.setup_connection_events()
        
        # Create performance indexes
        with next(get_db()) as db:
            postgresql_optimizer.create_indexes(db)
        
        logger.info("PostgreSQL optimizations initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize optimizations: {e}")

# Query optimization utilities
def optimize_booking_queries():
    """Specific optimizations for booking-related queries"""
    return {
        "use_indexes": [
            "idx_bookings_date_status",
            "idx_bookings_client_phone_partial"
        ],
        "recommended_filters": [
            "Always filter by date range for booking queries",
            "Use status filter to exclude cancelled bookings",
            "Consider using phone_normalized for phone searches"
        ]
    }

def optimize_calendar_queries():
    """Specific optimizations for calendar-related queries"""
    return {
        "use_indexes": [
            "idx_calendar_events_time_range",
            "idx_calendar_events_status_date"
        ],
        "recommended_filters": [
            "Always use time range filters (start_time, end_time)",
            "Filter by status for better performance",
            "Use BETWEEN for date range queries"
        ]
    }