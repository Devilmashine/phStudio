#!/usr/bin/env python3
"""
PostgreSQL Database Backup and Restore Script
Supports full backups, schema-only backups, and data-only backups
"""

import os
import sys
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import gzip
import shutil
from typing import Optional

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DatabaseBackup:
    """PostgreSQL database backup and restore utilities"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        
        # Parse database connection details
        self.db_params = self._parse_database_url()
        
    def _parse_database_url(self) -> dict:
        """Parse DATABASE_URL into connection parameters"""
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # postgresql://user:password@host:port/database
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
    
    def _get_pg_dump_env(self) -> dict:
        """Get environment variables for pg_dump"""
        env = os.environ.copy()
        if 'password' in self.db_params:
            env['PGPASSWORD'] = self.db_params['password']
        return env
    
    def backup_database(self, backup_type: str = 'full', compress: bool = True) -> Path:
        """Create database backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if backup_type == 'schema':
                filename = f'schema_backup_{timestamp}.sql'
                dump_args = ['--schema-only']
            elif backup_type == 'data':
                filename = f'data_backup_{timestamp}.sql'
                dump_args = ['--data-only']
            else:  # full backup
                filename = f'full_backup_{timestamp}.sql'
                dump_args = []
            
            backup_file = self.backup_dir / filename
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '-h', self.db_params.get('host', 'localhost'),
                '-p', self.db_params.get('port', '5432'),
                '-U', self.db_params.get('user', 'postgres'),
                '-d', self.db_params.get('database', 'phstudio'),
                '--verbose',
                '--no-password',
                '--format=custom' if compress else '--format=plain'
            ] + dump_args
            
            if not compress:
                cmd.extend(['-f', str(backup_file)])
            else:
                backup_file = backup_file.with_suffix('.dump')
                cmd.extend(['-f', str(backup_file)])
            
            logger.info(f"Starting {backup_type} backup to {backup_file}")
            
            # Execute pg_dump
            result = subprocess.run(
                cmd,
                env=self._get_pg_dump_env(),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Verify backup file exists and has content
                if backup_file.exists() and backup_file.stat().st_size > 0:
                    size_mb = backup_file.stat().st_size / (1024 * 1024)
                    logger.info(f"Backup created successfully: {backup_file} ({size_mb:.2f} MB)")
                    return backup_file
                else:
                    raise Exception("Backup file is empty or doesn't exist")
            else:
                raise Exception(f"pg_dump failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def restore_database(self, backup_file: Path, target_db: Optional[str] = None) -> bool:
        """Restore database from backup"""
        try:
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            target_database = target_db or self.db_params.get('database')
            
            logger.info(f"Restoring database {target_database} from {backup_file}")
            
            # Determine restore command based on file extension
            if backup_file.suffix == '.dump':
                # Custom format backup
                cmd = [
                    'pg_restore',
                    '-h', self.db_params.get('host', 'localhost'),
                    '-p', self.db_params.get('port', '5432'),
                    '-U', self.db_params.get('user', 'postgres'),
                    '-d', target_database,
                    '--verbose',
                    '--no-password',
                    '--clean',
                    '--if-exists',
                    str(backup_file)
                ]
            else:
                # Plain SQL backup
                cmd = [
                    'psql',
                    '-h', self.db_params.get('host', 'localhost'),
                    '-p', self.db_params.get('port', '5432'),
                    '-U', self.db_params.get('user', 'postgres'),
                    '-d', target_database,
                    '-f', str(backup_file)
                ]
            
            result = subprocess.run(
                cmd,
                env=self._get_pg_dump_env(),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Database restored successfully")
                return True
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def list_backups(self) -> list:
        """List available backup files"""
        backups = []
        for file in self.backup_dir.glob('*_backup_*.sql*'):
            stat = file.stat()
            backups.append({
                'file': file,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'type': 'full' if 'full_' in file.name else 
                       'schema' if 'schema_' in file.name else 'data'
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Remove backup files older than specified days"""
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 3600)
        removed = 0
        
        for backup in self.list_backups():
            if backup['created'].timestamp() < cutoff:
                backup['file'].unlink()
                logger.info(f"Removed old backup: {backup['file']}")
                removed += 1
        
        return removed

def main():
    """Main backup function"""
    if len(sys.argv) < 2:
        print("Usage: python backup_db.py <command> [options]")
        print("Commands:")
        print("  backup [full|schema|data] - Create backup (default: full)")
        print("  restore <backup_file> [target_db] - Restore from backup")
        print("  list - List available backups")
        print("  cleanup [days] - Remove backups older than N days (default: 30)")
        sys.exit(1)
    
    command = sys.argv[1]
    backup_manager = DatabaseBackup()
    
    try:
        if command == 'backup':
            backup_type = sys.argv[2] if len(sys.argv) > 2 else 'full'
            backup_file = backup_manager.backup_database(backup_type)
            print(f"Backup created: {backup_file}")
            
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("Error: backup file required")
                sys.exit(1)
            
            backup_file = Path(sys.argv[2])
            target_db = sys.argv[3] if len(sys.argv) > 3 else None
            
            success = backup_manager.restore_database(backup_file, target_db)
            sys.exit(0 if success else 1)
            
        elif command == 'list':
            backups = backup_manager.list_backups()
            if backups:
                print(f"{'File':<40} {'Type':<10} {'Size (MB)':<10} {'Created':<20}")
                print("-" * 80)
                for backup in backups:
                    print(f"{backup['file'].name:<40} {backup['type']:<10} {backup['size_mb']:<10.2f} {backup['created']:<20}")
            else:
                print("No backup files found")
                
        elif command == 'cleanup':
            keep_days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            removed = backup_manager.cleanup_old_backups(keep_days)
            print(f"Removed {removed} old backup files")
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

        # Удаляем старые бэкапы (оставляем только последние 5)
        backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir)])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(old_backup)
                logger.info(f"Removed old backup: {old_backup}")

    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        raise

if __name__ == '__main__':
    backup_database()
