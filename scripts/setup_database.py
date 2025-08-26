#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script
Handles database creation, user setup, and initial configuration
"""

import os
import sys
import logging
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """PostgreSQL database setup and management"""
    
    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'postgres')
        self.db_name = os.getenv('DB_NAME', 'phstudio')
        self.test_db_name = os.getenv('TEST_DB_NAME', 'phstudio_test')
        
        # Parse from DATABASE_URL if available
        database_url = os.getenv('DATABASE_URL')
        if database_url and database_url.startswith('postgresql://'):
            self._parse_database_url(database_url)
    
    def _parse_database_url(self, url: str):
        """Parse PostgreSQL URL to extract connection parameters"""
        try:
            # postgresql://user:password@host:port/database
            url = url.replace('postgresql://', '')
            if '@' in url:
                auth, host_db = url.split('@', 1)
                if ':' in auth:
                    self.db_user, self.db_password = auth.split(':', 1)
                
                if '/' in host_db:
                    host_port, self.db_name = host_db.split('/', 1)
                    if ':' in host_port:
                        self.db_host, self.db_port = host_port.split(':', 1)
                    else:
                        self.db_host = host_port
        except Exception as e:
            logger.warning(f"Failed to parse DATABASE_URL: {e}")
    
    def check_postgresql_service(self) -> bool:
        """Check if PostgreSQL service is running"""
        try:
            result = subprocess.run(
                ['pg_isready', '-h', self.db_host, '-p', self.db_port],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            logger.error("pg_isready command not found. Please install PostgreSQL client tools.")
            return False
    
    def create_database(self, db_name: str) -> bool:
        """Create database if it doesn't exist"""
        try:
            # Connect to postgres database to create new database
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                (db_name,)
            )
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                logger.info(f"Created database: {db_name}")
            else:
                logger.info(f"Database already exists: {db_name}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database {db_name}: {e}")
            return False
    
    def setup_databases(self) -> bool:
        """Setup main and test databases"""
        if not self.check_postgresql_service():
            logger.error("PostgreSQL service is not running or not accessible")
            return False
        
        logger.info("Setting up PostgreSQL databases...")
        
        # Create main database
        if not self.create_database(self.db_name):
            return False
        
        # Create test database
        if not self.create_database(self.test_db_name):
            return False
        
        logger.info("Database setup completed successfully")
        return True
    
    def run_migrations(self) -> bool:
        """Run Alembic migrations"""
        try:
            logger.info("Running database migrations...")
            
            # Change to project root directory
            os.chdir(project_root)
            
            # Run alembic migrations
            result = subprocess.run(
                ['alembic', 'upgrade', 'head'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Migrations completed successfully")
                return True
            else:
                logger.error(f"Migration failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            return False
    
    def create_admin_user(self) -> bool:
        """Create initial admin user"""
        try:
            from backend.app.core.database import get_db
            from backend.app.models.user import User, UserRole
            from passlib.context import CryptContext
            
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Get database session
            db = next(get_db())
            
            # Check if admin user exists
            admin_user = db.query(User).filter(User.username == "admin").first()
            
            if not admin_user:
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                hashed_password = pwd_context.hash(admin_password)
                
                admin_user = User(
                    username="admin",
                    email="admin@phstudio.local",
                    hashed_password=hashed_password,
                    role=UserRole.admin,
                    full_name="System Administrator"
                )
                
                db.add(admin_user)
                db.commit()
                
                logger.info(f"Created admin user with password: {admin_password}")
                logger.warning("Please change the admin password after first login!")
            else:
                logger.info("Admin user already exists")
            
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")
            return False
    
    def setup_complete_environment(self) -> bool:
        """Complete database environment setup"""
        logger.info("Starting complete database environment setup...")
        
        success = (
            self.setup_databases() and
            self.run_migrations() and
            self.create_admin_user()
        )
        
        if success:
            logger.info("Database environment setup completed successfully!")
            logger.info(f"Main database: {self.db_name}")
            logger.info(f"Test database: {self.test_db_name}")
            logger.info("You can now start the application")
        else:
            logger.error("Database setup failed. Please check the logs above.")
        
        return success

def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "setup"
    
    setup = DatabaseSetup()
    
    if command == "setup":
        success = setup.setup_complete_environment()
    elif command == "databases":
        success = setup.setup_databases()
    elif command == "migrate":
        success = setup.run_migrations()
    elif command == "admin":
        success = setup.create_admin_user()
    elif command == "check":
        success = setup.check_postgresql_service()
        if success:
            logger.info("PostgreSQL service is running")
        else:
            logger.error("PostgreSQL service is not accessible")
    else:
        logger.error(f"Unknown command: {command}")
        logger.info("Available commands: setup, databases, migrate, admin, check")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()