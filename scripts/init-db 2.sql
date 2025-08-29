-- PostgreSQL initialization script for Docker container
-- This script runs when the PostgreSQL container starts for the first time

-- Create test database
CREATE DATABASE photo_studio_test;

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Switch to main database
\c photo_studio;

-- Create extensions in main database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Switch to test database
\c photo_studio_test;

-- Create extensions in test database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Log successful completion
\echo 'Database initialization completed successfully'