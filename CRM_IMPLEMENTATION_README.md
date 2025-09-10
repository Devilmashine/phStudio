# Photo Studio Employee CRM Module - Implementation Guide

## Overview

This document provides comprehensive instructions for setting up, running, and using the enhanced Photo Studio Employee CRM Module. The system implements enterprise-grade architecture following FAANG engineering standards with domain-driven design, CQRS pattern, and event-driven architecture.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd phStudio

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Database Setup

```bash
# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/photostudio"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="your-secret-key-here"

# Initialize database
cd backend
alembic upgrade head

# Create admin user
python create_admin.py
```

### 3. Start Services

```bash
# Start Redis (if not using Docker)
redis-server

# Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in new terminal)
cd frontend
npm run dev
```

### 4. Using Docker (Alternative)

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app
```

## 🏗️ Architecture Overview

### Core Components

1. **Event Bus** (`backend/app/core/event_bus.py`)
   - In-memory and Redis-based event bus
   - Domain event publishing and subscription
   - Loose coupling between components

2. **CQRS Pattern** (`backend/app/core/cqrs.py`)
   - Command and Query Responsibility Segregation
   - Command/Query handlers and buses
   - Middleware support

3. **Result Pattern** (`backend/app/core/result.py`)
   - Functional error handling
   - Domain-specific error types
   - Chainable operations

4. **Enhanced Models** (`backend/app/models/`)
   - Base model with audit fields
   - Employee model with security features
   - Booking model with state machine

5. **Domain Services** (`backend/app/services/`)
   - Business logic implementation
   - Event emission and handling
   - Validation and business rules

6. **Security Service** (`backend/app/core/security.py`)
   - Multi-factor authentication
   - Rate limiting
   - Session management
   - Role-based access control

7. **Cache Service** (`backend/app/core/cache.py`)
   - Multi-layer caching (L1 in-memory, L2 Redis)
   - Distributed locking
   - Cache invalidation strategies

### Data Flow

```
Client Request → API Router → Domain Service → Repository → Database
                    ↓
              Event Bus → Event Handlers → Side Effects
                    ↓
              Cache Invalidation → Performance Optimization
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/photostudio
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379
REDIS_POOL_SIZE=10

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
MFA_ISSUER=PhotoStudio

# Application
DEBUG=true
LOG_LEVEL=INFO
CACHE_TTL=300
RATE_LIMIT_MAX_ATTEMPTS=5
RATE_LIMIT_WINDOW=300
```

### Database Configuration

```python
# backend/app/core/database.py
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": False
}
```

### Cache Configuration

```python
# backend/app/core/cache.py
CACHE_CONFIG = {
    "l1_max_size": 1000,
    "l1_ttl": 60,
    "l2_ttl": 300,
    "lock_timeout": 10,
    "lock_ttl": 30
}
```

## 📚 API Usage

### Authentication

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'

# Response includes access_token and refresh_token
```

### Booking Management

```bash
# Create booking
curl -X POST "http://localhost:8000/api/v1/bookings/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Doe",
    "client_phone": "+1234567890",
    "start_time": "2024-01-15T10:00:00Z",
    "end_time": "2024-01-15T12:00:00Z",
    "space_type": "studio_a",
    "people_count": 2
  }'

# Get bookings
curl -X GET "http://localhost:8000/api/v1/bookings/?date=2024-01-15" \
  -H "Authorization: Bearer <access_token>"

# Update booking state
curl -X POST "http://localhost:8000/api/v1/bookings/1/state" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "target_state": "confirmed",
    "reason": "Client confirmed via phone"
  }'
```

### Employee Management

```bash
# Get employee profile
curl -X GET "http://localhost:8000/api/v1/employees/profile" \
  -H "Authorization: Bearer <access_token>"

# Update employee
curl -X PUT "http://localhost:8000/api/v1/employees/1" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Admin",
    "department": "Management"
  }'
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_booking_domain_service.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run integration tests
pytest -m integration

# Run performance tests
pytest -m performance
```

### Frontend Testing

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### API Testing

```bash
# Test API endpoints
curl -X GET "http://localhost:8000/api/v1/bookings/health"

# Test with authentication
curl -X GET "http://localhost:8000/api/v1/bookings/" \
  -H "Authorization: Bearer <access_token>"
```

## 📊 Monitoring & Observability

### Metrics Collection

```python
# Prometheus metrics are automatically collected
# Access at: http://localhost:8000/metrics
```

### Logging

```python
# Structured logging is configured
# Logs are written to stdout and files
# Log level can be configured via LOG_LEVEL environment variable
```

### Health Checks

```bash
# Application health
curl "http://localhost:8000/health"

# Database health
curl "http://localhost:8000/health/db"

# Cache health
curl "http://localhost:8000/health/cache"
```

## 🔒 Security Features

### Multi-Factor Authentication (MFA)

1. **Enable MFA for Employee**
   ```python
   # Generate MFA secret
   secret = security_service.generate_mfa_secret()
   
   # Generate QR code
   qr_code = security_service.generate_mfa_qr_code(secret, username)
   
   # Enable MFA
   employee.enable_mfa(secret, backup_codes, user_id)
   ```

2. **MFA Authentication Flow**
   ```python
   # Login with MFA
   result = await security_service.authenticate(
       username="admin",
       password="password",
       mfa_code="123456"
   )
   ```

### Rate Limiting

```python
# Rate limiting is automatically applied
# Configuration in security service
RATE_LIMIT_CONFIG = {
    "max_attempts": 5,
    "window_seconds": 300,
    "lock_duration": 900
}
```

### Role-Based Access Control (RBAC)

```python
# Check permissions
if employee.has_permission("booking_management"):
    # Allow booking operations
    pass

# Check if can manage other employees
if employee.can_manage_employee(target_employee):
    # Allow management operations
    pass
```

## 🚀 Performance Optimization

### Caching Strategy

```python
# Multi-layer caching
@cached(ttl=300, key_prefix="bookings")
async def get_bookings_for_date(date: date):
    # L1: In-memory cache (60s TTL)
    # L2: Redis cache (300s TTL)
    # Fallback: Database query
    pass

# Cache invalidation
@cache_invalidate("booking:*")
async def update_booking():
    # Automatically invalidates related caches
    pass
```

### Database Optimization

```python
# Materialized views for analytics
await database_optimizer.create_materialized_views()

# Table partitioning for large tables
await database_optimizer.partition_large_tables()
```

### Query Optimization

```python
# Optimized queries with proper indexing
# Eager loading of relationships
# Query result caching
```

## 🔄 Event-Driven Architecture

### Domain Events

```python
# Events are automatically emitted
# BookingCreatedEvent
# BookingStateChangedEvent
# EmployeeLoginEvent

# Subscribe to events
async def handle_booking_created(event: BookingCreatedEvent):
    # Send notifications
    # Update analytics
    # Trigger workflows
    pass

await event_bus.subscribe(EventType.BOOKING_CREATED, handler)
```

### Event Handlers

```python
# Custom event handlers
class NotificationEventHandler(EventHandler):
    async def handle(self, event: DomainEvent):
        if event.event_type == EventType.BOOKING_CREATED:
            await self.send_booking_confirmation(event)
        elif event.event_type == EventType.BOOKING_STATE_CHANGED:
            await self.send_state_change_notification(event)
```

## 📈 Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  app:
    build: .
    deploy:
      replicas: 3
    environment:
      - REDIS_URL=redis://redis:6379
      - EVENT_BUS_TYPE=redis
```

### Database Scaling

```sql
-- Read replicas
-- Connection pooling
-- Query optimization
-- Proper indexing
```

### Cache Scaling

```python
# Redis cluster support
# Cache warming strategies
# Distributed locking across instances
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database status
   docker-compose ps postgres
   
   # Check connection
   python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"
   ```

2. **Redis Connection Errors**
   ```bash
   # Check Redis status
   redis-cli ping
   
   # Check Redis logs
   docker-compose logs redis
   ```

3. **Event Bus Issues**
   ```bash
   # Check event bus status
   curl "http://localhost:8000/health/events"
   
   # View event history
   # Access event bus logs
   ```

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start with debug logging
uvicorn app.main:app --reload --log-level debug
```

### Performance Issues

```bash
# Check cache hit rates
curl "http://localhost:8000/metrics"

# Monitor database performance
# Check slow query logs
# Analyze query execution plans
```

## 📚 Additional Resources

### Documentation

- [API Documentation](http://localhost:8000/docs) - Swagger UI
- [ReDoc Documentation](http://localhost:8000/redoc) - Alternative API docs
- [Architecture Decision Records](docs/adr/) - Design decisions

### Code Examples

- [Domain Services](backend/app/services/) - Business logic examples
- [API Endpoints](backend/app/api/routes/) - REST API examples
- [Event Handlers](backend/app/core/event_bus.py) - Event handling examples

### Testing Examples

- [Unit Tests](backend/tests/) - Comprehensive test coverage
- [Integration Tests](backend/tests/integration/) - API integration tests
- [Performance Tests](backend/tests/performance/) - Load testing examples

## 🤝 Contributing

### Development Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run code quality checks
pre-commit run --all-files

# Run tests before committing
pytest
npm test
```

### Code Standards

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write comprehensive tests
- Document all public APIs
- Follow domain-driven design principles

### Pull Request Process

1. Create feature branch
2. Implement changes with tests
3. Run all tests and quality checks
4. Update documentation
5. Submit pull request
6. Code review and approval
7. Merge to main branch

## 📞 Support

### Getting Help

- Check the troubleshooting section
- Review existing issues
- Create new issue with detailed description
- Contact development team

### Reporting Bugs

When reporting bugs, please include:
- Detailed error description
- Steps to reproduce
- Environment information
- Logs and stack traces
- Expected vs actual behavior

### Feature Requests

For feature requests, please include:
- Detailed use case description
- Business value
- Implementation suggestions
- Priority level

---

**Note**: This CRM module is designed for production use and follows enterprise-grade security and performance standards. Always test thoroughly in staging environments before deploying to production.
