#!/usr/bin/env python3
"""
PostgreSQL Database Maintenance Script
Handles optimization, statistics, and performance monitoring
"""

import os
import sys
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMaintenance:
    """PostgreSQL database maintenance and optimization"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.db_params = self._parse_database_url()
    
    def _parse_database_url(self) -> dict:
        """Parse DATABASE_URL into connection parameters"""
        url = self.database_url.replace('postgresql://', '')
        
        params = {}
        if '@' in url:
            auth, host_db = url.split('@', 1)
            if ':' in auth:
                params['user'], params['password'] = auth.split(':', 1)
            
            if '/' in host_db:
                host_port, params['database'] = host_db.split('/', 1)
                if ':' in host_port:
                    params['host'], params['port'] = host_port.split(':', 1)
                else:
                    params['host'] = host_port
                    params['port'] = '5432'
        
        return params
    
    def _get_psql_env(self) -> dict:
        """Get environment variables for psql"""
        env = os.environ.copy()
        if 'password' in self.db_params:
            env['PGPASSWORD'] = self.db_params['password']
        return env
    
    def _execute_sql(self, sql: str) -> str:
        """Execute SQL command and return output"""
        cmd = [
            'psql',
            '-h', self.db_params.get('host', 'localhost'),
            '-p', self.db_params.get('port', '5432'),
            '-U', self.db_params.get('user', 'postgres'),
            '-d', self.db_params.get('database', 'phstudio'),
            '-c', sql
        ]
        
        result = subprocess.run(
            cmd,
            env=self._get_psql_env(),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"SQL execution failed: {result.stderr}")
        
        return result.stdout
    
    def vacuum_analyze(self, full: bool = False) -> bool:
        """Run VACUUM and ANALYZE on all tables"""
        try:
            logger.info("Starting VACUUM and ANALYZE operations...")
            
            if full:
                logger.info("Running VACUUM FULL (this may take a while)...")
                self._execute_sql("VACUUM FULL;")
            else:
                logger.info("Running regular VACUUM...")
                self._execute_sql("VACUUM;")
            
            logger.info("Running ANALYZE...")
            self._execute_sql("ANALYZE;")
            
            logger.info("VACUUM and ANALYZE completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"VACUUM/ANALYZE failed: {e}")
            return False
    
    def reindex_database(self) -> bool:
        """Rebuild all indexes in the database"""
        try:
            logger.info("Starting database reindex...")
            
            # Get list of tables
            tables_sql = """
                SELECT schemaname, tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """
            
            output = self._execute_sql(tables_sql)
            
            # Parse table names
            tables = []
            for line in output.strip().split('\n')[2:]:  # Skip header lines
                if '|' in line and 'public' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 2:
                        tables.append(parts[1])
            
            # Reindex each table
            for table in tables:
                if table and table != '':
                    logger.info(f"Reindexing table: {table}")
                    self._execute_sql(f"REINDEX TABLE {table};")
            
            logger.info("Database reindex completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Reindex failed: {e}")
            return False
    
    def update_statistics(self) -> bool:
        """Update table statistics for query planner"""
        try:
            logger.info("Updating table statistics...")
            
            # Update statistics on all tables
            self._execute_sql("ANALYZE;")
            
            # Update extended statistics if available (PostgreSQL 10+)
            try:
                self._execute_sql("SELECT pg_stat_reset();")
                logger.info("Statistics reset and updated")
            except:
                logger.warning("Could not reset statistics (may not be supported)")
            
            logger.info("Statistics update completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Statistics update failed: {e}")
            return False
    
    def check_database_size(self) -> Dict[str, Any]:
        """Check database and table sizes"""
        try:
            # Database size
            db_size_sql = """
                SELECT pg_size_pretty(pg_database_size(current_database())) as database_size
            """
            db_size = self._execute_sql(db_size_sql).strip().split('\n')[2].strip()
            
            # Table sizes
            table_sizes_sql = """
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """
            
            table_output = self._execute_sql(table_sizes_sql)
            
            return {
                "database_size": db_size,
                "table_sizes_output": table_output,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Size check failed: {e}")
            return {}
    
    def check_slow_queries(self) -> str:
        """Check for slow queries (requires pg_stat_statements extension)"""
        try:
            slow_queries_sql = """
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                ORDER BY mean_time DESC 
                LIMIT 10
            """
            
            return self._execute_sql(slow_queries_sql)
            
        except Exception as e:
            logger.warning(f"Could not check slow queries: {e}")
            logger.info("Consider installing pg_stat_statements extension for query analysis")
            return ""
    
    def check_index_usage(self) -> str:
        """Check index usage statistics"""
        try:
            index_usage_sql = """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_tup_read DESC
            """
            
            return self._execute_sql(index_usage_sql)
            
        except Exception as e:
            logger.error(f"Index usage check failed: {e}")
            return ""
    
    def check_connection_stats(self) -> str:
        """Check database connection statistics"""
        try:
            conn_stats_sql = """
                SELECT 
                    datname,
                    numbackends,
                    xact_commit,
                    xact_rollback,
                    blks_read,
                    blks_hit,
                    tup_returned,
                    tup_fetched,
                    tup_inserted,
                    tup_updated,
                    tup_deleted
                FROM pg_stat_database 
                WHERE datname = current_database()
            """
            
            return self._execute_sql(conn_stats_sql)
            
        except Exception as e:
            logger.error(f"Connection stats check failed: {e}")
            return ""
    
    def generate_maintenance_report(self) -> str:
        """Generate comprehensive maintenance report"""
        logger.info("Generating maintenance report...")
        
        report = []
        report.append("=" * 80)
        report.append(f"PostgreSQL Database Maintenance Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Database: {self.db_params.get('database', 'unknown')}")
        report.append("=" * 80)
        
        # Database size information
        size_info = self.check_database_size()
        if size_info:
            report.append("\n--- DATABASE SIZE ---")
            report.append(f"Total Size: {size_info.get('database_size', 'unknown')}")
            report.append("\n--- TABLE SIZES ---")
            report.append(size_info.get('table_sizes_output', 'No data available'))
        
        # Connection statistics
        report.append("\n--- CONNECTION STATISTICS ---")
        conn_stats = self.check_connection_stats()
        if conn_stats:
            report.append(conn_stats)
        
        # Index usage
        report.append("\n--- INDEX USAGE ---")
        index_stats = self.check_index_usage()
        if index_stats:
            report.append(index_stats)
        
        # Slow queries
        slow_queries = self.check_slow_queries()
        if slow_queries:
            report.append("\n--- SLOW QUERIES ---")
            report.append(slow_queries)
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def full_maintenance(self) -> bool:
        """Run full maintenance routine"""
        logger.info("Starting full database maintenance...")
        
        success = True
        
        # Update statistics
        if not self.update_statistics():
            success = False
        
        # Run VACUUM and ANALYZE
        if not self.vacuum_analyze():
            success = False
        
        # Generate report
        try:
            report = self.generate_maintenance_report()
            
            # Save report to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = f"maintenance_report_{timestamp}.txt"
            
            with open(report_file, 'w') as f:
                f.write(report)
            
            logger.info(f"Maintenance report saved to: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            success = False
        
        if success:
            logger.info("Full maintenance completed successfully")
        else:
            logger.error("Maintenance completed with errors")
        
        return success

def main():
    """Main maintenance function"""
    if len(sys.argv) < 2:
        print("Usage: python maintain_db.py <command>")
        print("Commands:")
        print("  vacuum - Run VACUUM and ANALYZE")
        print("  vacuum-full - Run VACUUM FULL and ANALYZE")
        print("  reindex - Rebuild all database indexes")
        print("  stats - Update table statistics")
        print("  report - Generate maintenance report")
        print("  full - Run full maintenance (recommended weekly)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        maintenance = DatabaseMaintenance()
        
        if command == 'vacuum':
            success = maintenance.vacuum_analyze(full=False)
        elif command == 'vacuum-full':
            success = maintenance.vacuum_analyze(full=True)
        elif command == 'reindex':
            success = maintenance.reindex_database()
        elif command == 'stats':
            success = maintenance.update_statistics()
        elif command == 'report':
            report = maintenance.generate_maintenance_report()
            print(report)
            success = True
        elif command == 'full':
            success = maintenance.full_maintenance()
        else:
            print(f"Unknown command: {command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Maintenance operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()