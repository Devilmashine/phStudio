"""
Database optimization utilities for phStudio application.

This module provides query optimization, performance monitoring, and database
maintenance utilities for PostgreSQL.
"""

from sqlalchemy import text, inspect, Index
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import time
from contextlib import contextmanager

from app.core.database import get_db
from app.models.booking import Booking
from app.models.user import User
from app.models.calendar_event import CalendarEvent

logger = logging.getLogger(__name__)


class QueryPerformanceMonitor:
    """Monitor and log database query performance"""
    
    def __init__(self, threshold_ms: float = 100.0):
        self.threshold_ms = threshold_ms
        self.slow_queries = []
    
    @contextmanager
    def monitor_query(self, query_name: str, query: str):
        """Context manager to monitor query execution time"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = (time.time() - start_time) * 1000
            
            if execution_time > self.threshold_ms:
                logger.warning(
                    f"Slow query detected: {query_name} took {execution_time:.2f}ms"
                )
                self.slow_queries.append({
                    'query_name': query_name,
                    'query': query,
                    'execution_time_ms': execution_time,
                    'timestamp': datetime.utcnow()
                })
            else:
                logger.debug(f"Query {query_name} completed in {execution_time:.2f}ms")


class DatabaseOptimizer:
    """Database optimization utilities and maintenance"""
    
    def __init__(self, db: Session):
        self.db = db
        self.performance_monitor = QueryPerformanceMonitor()
    
    def analyze_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """Analyze table statistics for optimization insights"""
        try:
            with self.performance_monitor.monitor_query(
                f"analyze_table_stats_{table_name}",
                f"SELECT * FROM pg_stat_user_tables WHERE relname = '{table_name}'"
            ):
                result = self.db.execute(text("""
                    SELECT 
                        schemaname,
                        relname,
                        seq_scan,
                        seq_tup_read,
                        idx_scan,
                        idx_tup_fetch,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del,
                        n_live_tup,
                        n_dead_tup,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables 
                    WHERE relname = :table_name
                """), {"table_name": table_name}).fetchone()
                
                if result:
                    return {
                        "table_name": result.relname,
                        "sequential_scans": result.seq_scan,
                        "sequential_tuples_read": result.seq_tup_read,
                        "index_scans": result.idx_scan,
                        "index_tuples_fetched": result.idx_tup_fetch,
                        "inserts": result.n_tup_ins,
                        "updates": result.n_tup_upd,
                        "deletes": result.n_tup_del,
                        "live_tuples": result.n_live_tup,
                        "dead_tuples": result.n_dead_tup,
                        "last_vacuum": result.last_vacuum,
                        "last_analyze": result.last_analyze,
                        "scan_ratio": (
                            result.idx_scan / (result.seq_scan + result.idx_scan)
                            if (result.seq_scan + result.idx_scan) > 0 else 0
                        )
                    }
                return {}
        except Exception as e:
            logger.error(f"Error analyzing table statistics for {table_name}: {e}")
            return {}
    
    def get_unused_indexes(self) -> List[Dict[str, Any]]:
        """Identify potentially unused indexes"""
        try:
            with self.performance_monitor.monitor_query("unused_indexes", "pg_stat_user_indexes"):
                result = self.db.execute(text("""
                    SELECT 
                        schemaname,
                        relname as table_name,
                        indexrelname as index_name,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    WHERE idx_scan < 10
                    ORDER BY idx_scan ASC
                """)).fetchall()
                
                return [
                    {
                        "schema": row.schemaname,
                        "table_name": row.table_name,
                        "index_name": row.index_name,
                        "scans": row.idx_scan,
                        "tuples_read": row.idx_tup_read,
                        "tuples_fetched": row.idx_tup_fetch
                    }
                    for row in result
                ]
        except Exception as e:
            logger.error(f"Error identifying unused indexes: {e}")
            return []
    
    def get_missing_indexes_suggestions(self) -> List[Dict[str, Any]]:
        """Suggest missing indexes based on query patterns"""
        suggestions = []
        
        try:
            # Check for sequential scans on large tables
            large_tables = self.db.execute(text("""
                SELECT 
                    schemaname,
                    relname,
                    seq_scan,
                    seq_tup_read,
                    n_live_tup
                FROM pg_stat_user_tables 
                WHERE seq_scan > 100 
                AND n_live_tup > 1000
                ORDER BY seq_scan DESC
            """)).fetchall()
            
            for table in large_tables:
                suggestions.append({
                    "type": "high_sequential_scans",
                    "table": table.relname,
                    "sequential_scans": table.seq_scan,
                    "live_tuples": table.n_live_tup,
                    "recommendation": f"Consider adding indexes to frequently queried columns in {table.relname}"
                })
                
        except Exception as e:
            logger.error(f"Error generating index suggestions: {e}")
        
        return suggestions
    
    def optimize_booking_queries(self) -> Dict[str, Any]:
        """Optimize common booking queries"""
        optimization_results = {}
        
        try:
            # Optimize date range queries
            with self.performance_monitor.monitor_query("booking_date_range", "booking optimization"):
                # Ensure we have proper indexes for date range queries
                date_range_query = """
                EXPLAIN (ANALYZE, BUFFERS) 
                SELECT * FROM bookings 
                WHERE start_time >= NOW() - INTERVAL '30 days'
                AND end_time <= NOW() + INTERVAL '30 days'
                """
                result = self.db.execute(text(date_range_query)).fetchall()
                optimization_results["date_range_query"] = [row[0] for row in result]
            
            # Optimize status-based queries
            with self.performance_monitor.monitor_query("booking_status", "status optimization"):
                status_query = """
                EXPLAIN (ANALYZE, BUFFERS)
                SELECT * FROM bookings 
                WHERE status = 'pending'
                ORDER BY start_time ASC
                """
                result = self.db.execute(text(status_query)).fetchall()
                optimization_results["status_query"] = [row[0] for row in result]
            
            # Optimize client search queries
            with self.performance_monitor.monitor_query("client_search", "client optimization"):
                client_query = """
                EXPLAIN (ANALYZE, BUFFERS)
                SELECT * FROM bookings 
                WHERE client_phone LIKE '%123%'
                OR client_name ILIKE '%test%'
                """
                result = self.db.execute(text(client_query)).fetchall()
                optimization_results["client_search_query"] = [row[0] for row in result]
                
        except Exception as e:
            logger.error(f"Error optimizing booking queries: {e}")
            optimization_results["error"] = str(e)
        
        return optimization_results
    
    def create_optimized_indexes(self) -> Dict[str, bool]:
        """Create additional optimized indexes based on usage patterns"""
        index_results = {}
        
        try:
            # Composite index for booking date and status queries
            composite_index_sql = """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_date_status_optimized
            ON bookings (date, status, start_time)
            WHERE status IN ('pending', 'confirmed')
            """
            
            self.db.execute(text(composite_index_sql))
            index_results["composite_date_status"] = True
            logger.info("Created optimized composite index for bookings")
            
            # Partial index for active users
            user_active_sql = """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_optimized
            ON users (username, role)
            WHERE is_active = 'true'
            """
            
            self.db.execute(text(user_active_sql))
            index_results["user_active_partial"] = True
            logger.info("Created optimized partial index for active users")
            
            # Text search index for client names (using trigram)
            try:
                # Enable pg_trgm extension if not exists
                self.db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
                
                client_search_sql = """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_client_name_trgm
                ON bookings 
                USING GIN (client_name gin_trgm_ops)
                """
                
                self.db.execute(text(client_search_sql))
                index_results["client_name_search"] = True
                logger.info("Created trigram index for client name search")
                
            except Exception as e:
                logger.warning(f"Could not create trigram index: {e}")
                index_results["client_name_search"] = False
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creating optimized indexes: {e}")
            self.db.rollback()
            index_results["error"] = str(e)
        
        return index_results
    
    def vacuum_analyze_tables(self) -> Dict[str, bool]:
        """Perform vacuum and analyze on key tables"""
        vacuum_results = {}
        
        try:
            # Note: VACUUM cannot be run inside a transaction block
            # These would need to be run separately in production
            tables = ["bookings", "users", "calendar_events"]
            
            for table in tables:
                try:
                    # Analyze to update statistics
                    self.db.execute(text(f"ANALYZE {table}"))
                    vacuum_results[f"analyze_{table}"] = True
                    logger.info(f"Analyzed table {table}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing table {table}: {e}")
                    vacuum_results[f"analyze_{table}"] = False
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error in vacuum/analyze operations: {e}")
            vacuum_results["error"] = str(e)
        
        return vacuum_results
    
    def get_database_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive database performance report"""
        report = {
            "timestamp": datetime.utcnow(),
            "table_statistics": {},
            "unused_indexes": [],
            "missing_index_suggestions": [],
            "query_optimization": {},
            "slow_queries": self.performance_monitor.slow_queries
        }
        
        try:
            # Analyze key tables
            for table in ["bookings", "users", "calendar_events"]:
                report["table_statistics"][table] = self.analyze_table_statistics(table)
            
            # Get unused indexes
            report["unused_indexes"] = self.get_unused_indexes()
            
            # Get missing index suggestions
            report["missing_index_suggestions"] = self.get_missing_indexes_suggestions()
            
            # Optimize queries
            report["query_optimization"] = self.optimize_booking_queries()
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            report["error"] = str(e)
        
        return report


def get_database_optimizer(db: Session = None) -> DatabaseOptimizer:
    """Factory function to get database optimizer instance"""
    if db is None:
        db = next(get_db())
    return DatabaseOptimizer(db)


def run_database_maintenance() -> Dict[str, Any]:
    """Run comprehensive database maintenance tasks"""
    db = next(get_db())
    optimizer = DatabaseOptimizer(db)
    
    maintenance_results = {
        "start_time": datetime.utcnow(),
        "tasks": {}
    }
    
    try:
        # Create optimized indexes
        maintenance_results["tasks"]["index_creation"] = optimizer.create_optimized_indexes()
        
        # Vacuum and analyze
        maintenance_results["tasks"]["vacuum_analyze"] = optimizer.vacuum_analyze_tables()
        
        # Generate performance report
        maintenance_results["tasks"]["performance_report"] = optimizer.get_database_performance_report()
        
        maintenance_results["status"] = "completed"
        maintenance_results["end_time"] = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Database maintenance failed: {e}")
        maintenance_results["status"] = "failed"
        maintenance_results["error"] = str(e)
        maintenance_results["end_time"] = datetime.utcnow()
    
    finally:
        db.close()
    
    return maintenance_results