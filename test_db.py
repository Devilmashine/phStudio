import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection"""
    try:
        # Database connection parameters
        conn_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'photo_studio',
            'user': 'postgres',
            'password': ''
        }
        
        # Try to connect to the database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Close connections
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()