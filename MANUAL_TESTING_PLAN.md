# Manual Testing Plan for Photo Studio CRM

## 🎯 Objective
To manually test the Photo Studio CRM system to ensure all components are working correctly after development completion.

## 📋 Prerequisites
- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL client
- Git

## ⚙️ Setup Instructions

### 1. Environment Setup

#### Create Environment Files
```bash
# Copy development environment template
cp .env.development.template .env

# Edit .env file with actual values
# Make sure to update:
# - SECRET_KEY with a secure random key
# - TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID if using Telegram integration
```

#### Install Backend Dependencies
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt

# Install performance testing dependencies (optional)
pip3 install -r requirements-performance.txt
```

#### Install Frontend Dependencies
```bash
# From project root
npm install
```

### 2. Database Setup

#### Using Docker Compose (Recommended)
```bash
# Start database services
docker-compose up -d db redis

# Wait for services to be ready
docker-compose ps

# Initialize database
docker-compose exec db psql -U postgres -d photo_studio -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
```

#### Manual Database Setup (Alternative)
```bash
# If you have PostgreSQL installed locally
createdb photo_studio
psql -d photo_studio -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
```

### 3. Database Migration
```bash
# Navigate to backend directory
cd backend

# Run migrations
alembic upgrade head
```

## ▶️ Running the Application

### Option 1: Using Docker Compose (Recommended for testing)
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Manual Start

#### Start Backend
```bash
# Navigate to backend directory
cd backend

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

#### Start Frontend
```bash
# From project root
npm run dev
```

## 🧪 Manual Testing Checklist

### 1. Backend API Testing

#### Health Checks
- [ ] GET `/api/health` - Basic health check
- [ ] GET `/api/health/detailed` - Detailed health check
- [ ] GET `/api/health/database` - Database health check
- [ ] GET `/api/health/ready` - Readiness probe
- [ ] GET `/api/health/live` - Liveness probe

#### Authentication
- [ ] POST `/api/auth/login` - Login with test user
- [ ] POST `/api/auth/logout` - Logout
- [ ] GET `/api/auth/me` - Get current user info
- [ ] POST `/api/auth/refresh` - Refresh token

#### Bookings
- [ ] GET `/api/bookings/` - List bookings
- [ ] POST `/api/bookings/` - Create new booking
- [ ] GET `/api/bookings/{id}` - Get specific booking
- [ ] PUT `/api/bookings/{id}` - Update booking
- [ ] DELETE `/api/bookings/{id}` - Delete booking
- [ ] GET `/api/bookings/calendar` - Calendar view
- [ ] GET `/api/bookings/stats` - Booking statistics

#### Employees
- [ ] GET `/api/employees/` - List employees
- [ ] POST `/api/employees/` - Create employee
- [ ] GET `/api/employees/{id}` - Get employee
- [ ] PUT `/api/employees/{id}` - Update employee
- [ ] DELETE `/api/employees/{id}` - Delete employee

#### Calendar
- [ ] GET `/api/calendar/` - Get calendar events
- [ ] POST `/api/calendar/` - Create calendar event
- [ ] PUT `/api/calendar/{id}` - Update calendar event
- [ ] DELETE `/api/calendar/{id}` - Delete calendar event

#### Monitoring
- [ ] GET `/api/monitoring/metrics` - Prometheus metrics
- [ ] GET `/api/monitoring/health/application` - Application health
- [ ] GET `/api/monitoring/metrics/summary` - Metrics summary
- [ ] GET `/api/monitoring/dashboard` - Monitoring dashboard

### 2. Frontend Testing

#### Public Pages
- [ ] Home page loads correctly
- [ ] Booking form accessible
- [ ] Gallery page displays images
- [ ] News page shows articles
- [ ] Contact form works

#### Authentication Flow
- [ ] Login page displays correctly
- [ ] User can log in with valid credentials
- [ ] Error messages shown for invalid login
- [ ] User redirected to dashboard after login

#### Admin Dashboard
- [ ] Dashboard loads with statistics
- [ ] Booking management works
- [ ] Employee management functions
- [ ] Calendar view displays correctly
- [ ] Settings can be updated

#### Booking Flow
- [ ] Step 1: Date and time selection
- [ ] Step 2: Client information
- [ ] Step 3: Booking details and equipment
- [ ] Step 4: Terms and conditions
- [ ] Step 5: Confirmation and submission
- [ ] Success message after booking

#### Enhanced Features
- [ ] Kanban board displays bookings
- [ ] Drag and drop functionality works
- [ ] Real-time updates with WebSocket
- [ ] Dark mode toggle
- [ ] Responsive design on mobile

### 3. Integration Testing

#### Database Integration
- [ ] Bookings are saved to database
- [ ] Employee data persists
- [ ] Calendar events stored correctly
- [ ] User sessions managed properly

#### Redis Integration
- [ ] Caching working for frequent queries
- [ ] Session storage in Redis
- [ ] Rate limiting functioning

#### External Services
- [ ] Telegram notifications (if configured)
- [ ] Email sending (if configured)
- [ ] Third-party API integrations

### 4. Performance Testing

#### Response Times
- [ ] API responses under 500ms for most endpoints
- [ ] Database queries optimized
- [ ] Frontend loads within 3 seconds

#### Concurrent Users
- [ ] System handles multiple simultaneous users
- [ ] No database connection issues
- [ ] Memory usage remains stable

### 5. Security Testing

#### Authentication
- [ ] Protected routes require authentication
- [ ] JWT tokens expire correctly
- [ ] Passwords properly hashed
- [ ] Session management secure

#### Authorization
- [ ] Role-based access control working
- [ ] Users can only access permitted resources
- [ ] Admin functions restricted to authorized users

#### Input Validation
- [ ] Form validation works correctly
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] File upload security

## 🛠️ Troubleshooting Common Issues

### Database Connection Issues
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test database connection
docker-compose exec db pg_isready -U postgres -d photo_studio
```

### Redis Connection Issues
```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Backend Startup Issues
```bash
# Check backend logs
docker-compose logs api

# Or if running manually
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

### Frontend Issues
```bash
# Check frontend build
npm run build

# Check for TypeScript errors
npm run lint
```

## 📊 Expected Results

### Success Criteria
- All API endpoints return correct HTTP status codes
- Frontend components render without errors
- Database operations complete successfully
- User authentication and authorization work correctly
- Real-time features function as expected
- Performance meets requirements (<500ms response time)
- No security vulnerabilities detected

### Failure Indicators
- HTTP 500 errors from API endpoints
- Frontend components fail to load
- Database connection failures
- Authentication bypass or privilege escalation
- Memory leaks or performance degradation
- Security vulnerabilities

## 📝 Test Data Preparation

### Create Test Users
```bash
# Navigate to backend directory
cd backend

# Create admin user
python3 create_admin.py

# Create test users
python3 create_test_users.py

# Populate with test data
python3 populate_test_data.py
```

### Sample Booking Data
```json
{
  "client_name": "Test Client",
  "client_phone": "+1234567890",
  "client_email": "test@example.com",
  "booking_date": "2024-02-15",
  "start_time": "10:00",
  "end_time": "12:00",
  "space_type": "main_studio",
  "total_price": 5000
}
```

## 🎉 Completion

After completing all tests successfully, the Photo Studio CRM system is ready for production use. Document any issues found and create tickets for fixes if needed.

## 📞 Support

If you encounter any issues during testing, please check:
1. All environment variables are correctly set
2. Database and Redis services are running
3. Network connectivity between services
4. Required ports are available
5. Sufficient system resources (RAM, CPU, Disk)