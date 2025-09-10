import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

def test_postgresql_connection():
    """Test basic PostgreSQL connection"""
    settings = get_settings()
    
    # Use the test database URL
    engine = create_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()
        assert version is not None
        assert "PostgreSQL" in version[0]
    
    engine.dispose()


def test_postgresql_enhanced_types():
    """Test PostgreSQL-specific data types"""
    settings = get_settings()
    
    # Use the test database URL
    engine = create_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )
    
    # Create a simple table with PostgreSQL-specific types
    with engine.connect() as conn:
        # Create test table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS test_pg_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                metadata JSONB,
                tags TEXT[]
            )
        """))
        
        # Insert test data
        conn.execute(text("""
            INSERT INTO test_pg_types (name, metadata, tags) 
            VALUES 
                ('test1', '{"key": "value"}', ARRAY['tag1', 'tag2']),
                ('test2', '{"count": 42}', ARRAY['tag3', 'tag4'])
        """))
        
        # Query data
        result = conn.execute(text("SELECT * FROM test_pg_types WHERE name = 'test1'"))
        row = result.fetchone()
        
        assert row is not None
        assert row.name == 'test1'
        assert row.is_active is True
        
        # Clean up
        conn.execute(text("DROP TABLE test_pg_types"))
        
        conn.commit()
    
    engine.dispose()