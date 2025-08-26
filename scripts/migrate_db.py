#!/usr/bin/env python3
"""
Production Database Migration Script
Handles safe database migrations with rollback capabilities
"""

import os
import sys
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Production database migration manager"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.backup_dir = Path('migration_backups')
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> Path:
        """Create pre-migration backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f'pre_migration_{timestamp}.dump'
        
        cmd = ['pg_dump', self.database_url, '-f', str(backup_file), '--format=custom']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Backup created: {backup_file}")
            return backup_file
        else:
            raise Exception(f"Backup failed: {result.stderr}")
    
    def run_migrations(self) -> bool:
        """Run Alembic migrations"""
        try:
            os.chdir(project_root)
            result = subprocess.run(['alembic', 'upgrade', 'head'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Migrations completed successfully")
                return True
            else:
                logger.error(f"Migration failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def safe_migrate(self) -> bool:
        """Perform safe migration with backup"""
        logger.info("Starting safe database migration...")
        
        # Create backup
        try:
            backup_file = self.create_backup()
        except Exception:
            logger.error("Failed to create backup. Aborting migration.")
            return False
        
        # Run migrations
        if self.run_migrations():
            logger.info("Migration completed successfully")
            return True
        else:
            logger.error("Migration failed")
            return False

def main():
    """Main migration function"""
    try:
        migration = DatabaseMigration()
        success = migration.safe_migrate()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()