# Employee CRM Module Design Document

## 1. Overview

This document outlines the design for replacing the existing admin panel with a comprehensive Employee CRM module. The new system will function as a full business and project management CRM with both business functions and administrative capabilities, focusing on booking management through a Kanban-style interface. The underlying booking functionality will remain unchanged as it is working perfectly. Clients do not have user accounts and all bookings are made as guest transactions.

### 1.1 Objectives

- Remove the existing admin panel and replace it with a modern Employee CRM system
- Implement a Kanban-style booking management interface as the primary way to manage events
- Maintain minimal client data storage (names, phones, and optional emails) in compliance with Russian legislation. Clients do not have user accounts.
- Implement a role-based access control system for employees only (owner, admin, manager, employee roles)
- Restrict employee account creation to only admin and owner roles
- Implement full employee account lifecycle management
- Ensure FAANG-level quality standards with budget-conscious development using free/self-hosted services
- Preserve existing booking functionality as it is working perfectly

### 1.2 Key Features

- Kanban-style booking management dashboard
- Role-based access control (RBAC) for employees only (owner, admin, manager, employee roles)
- Minimal client data storage (names, phones, and optional emails). Clients do not have user accounts.
- Employee account lifecycle management
- Legal compliance with Russian Federal Law 152-FZ
- Modern, responsive UI with dark mode support
- Comprehensive audit logging
- Telegram integration for booking notifications using the new queue-based system

## 2. Architecture

### 2.1 System Architecture

The Employee CRM module will follow a modern microservices-inspired architecture within the existing monolithic application:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend (React)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │   Kanban Board  │  │  User Mgmt UI   │  │  Booking Mgmt UI    │ │
│  │   Component     │  │   Component     │  │   Component         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                        API Layer (FastAPI)                          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  Booking API    │  │   User API      │  │  Calendar API       │ │
│  │   Routes        │  │   Routes        │  │   Routes            │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  Booking Svc    │  │   User Svc      │  │  Calendar Svc       │ │
│  │                 │  │                 │  │                     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                      Data Layer (PostgreSQL)                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  Bookings       │  │   Users         │  │  Calendar Events    │ │
│  │   Table         │  │   Table         │  │   Table             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  Clients        │  │   Employees     │  │  Legal Documents    │ │
│  │   Table         │  │   Table         │  │   Table             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

- **Frontend**: React with TypeScript, Tailwind CSS, React Query
- **Backend**: FastAPI with Python 3.9+
- **Database**: PostgreSQL 13+
- **Authentication**: JWT with refresh tokens
- **Deployment**: Docker with Docker Compose
- **Monitoring**: Built-in logging and metrics

## 3. API Endpoints Reference

### 3.1 Authentication & User Management

#### User Authentication
- `POST /api/auth/login` - Employee login
- `POST /api/auth/logout` - Employee logout
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

#### Employee Account Management (Admin/Owner only)
- `POST /api/users` - Create new employee account
- `GET /api/users` - List all employees
- `GET /api/users/{id}` - Get employee details
- `PUT /api/users/{id}` - Update employee account
- `DELETE /api/users/{id}` - Delete employee account
- `PATCH /api/users/{id}/status` - Activate/deactivate employee account
- `PATCH /api/users/{id}/role` - Change employee role
- `POST /api/users/{id}/reset-password` - Reset employee password

Note: This API is exclusively for managing employee accounts. Clients do not have user accounts in the system.

### 3.2 Booking Management

#### Booking Operations
- `GET /api/bookings` - List all bookings (with date range and status filters)
- `GET /api/bookings/{id}` - Get booking details
- `POST /api/bookings` - Create new booking with validation
- `PUT /api/bookings/{id}` - Update booking
- `DELETE /api/bookings/{id}` - Delete booking
- `PATCH /api/bookings/{id}/status` - Update booking status

#### Booking Status Management
- `GET /api/bookings/statuses` - Get available booking statuses
- `PATCH /api/bookings/{id}/confirm` - Confirm booking
- `PATCH /api/bookings/{id}/cancel` - Cancel booking
- `PATCH /api/bookings/{id}/complete` - Mark booking as completed

All booking operations will maintain the existing comprehensive validation and error handling as implemented in the `BookingService` class, including time conflict detection, full-hour validation, and required field validation. The underlying booking functionality will remain unchanged as it is working perfectly.

### 3.3 Calendar Management

#### Calendar Events
- `GET /api/calendar-events` - List calendar events
- `GET /api/calendar-events/{id}` - Get calendar event details
- `POST /api/calendar-events` - Create calendar event
- `PUT /api/calendar-events/{id}` - Update calendar event
- `DELETE /api/calendar-events/{id}` - Delete calendar event
- `PATCH /api/calendar-events/{id}/status` - Update event status

#### Calendar Availability
- `GET /api/calendar/availability` - Get calendar availability
- `POST /api/calendar/availability` - Set calendar availability

### 3.4 Kanban Board Operations

#### Board Management
- `GET /api/kanban/board` - Get Kanban board data
- `POST /api/kanban/columns` - Create new column
- `PUT /api/kanban/columns/{id}` - Update column
- `DELETE /api/kanban/columns/{id}` - Delete column

#### Card Operations
- `POST /api/kanban/cards` - Create new card
- `PUT /api/kanban/cards/{id}` - Update card
- `DELETE /api/kanban/cards/{id}` - Delete card
- `PATCH /api/kanban/cards/{id}/move` - Move card between columns

### 3.5 Legal Compliance

#### Consent Management
- `POST /api/consent/cookie-consent/record` - Record cookie consent
- `GET /api/consent/cookie-consent/categories` - Get cookie categories
- `GET /api/consent/cookie-consent/preferences/{user_identifier}` - Get user preferences
- `POST /api/consent/booking-consent/record` - Record booking consent
- `GET /api/consent/summary/{user_identifier}` - Get consent summary
- `POST /api/consent/withdraw` - Withdraw consent

#### Legal Documents
- `GET /api/documents/active` - Get all active legal documents
- `GET /api/documents/{document_type}/current` - Get current document version
- `GET /api/documents/{document_type}/history` - Get document version history

## 4. Data Models & ORM Mapping

### 4.1 User Model (Employees Only)

```python
class UserRole(str, Enum):
    employee = "employee"  # Regular employee role
    manager = "manager"
    admin = "admin"
    owner = "owner"  # Business owner role

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.employee)
    full_name = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    ical_token = Column(String(64), unique=True, nullable=True)
    is_active = Column(String(5), default="true", nullable=False)
    phone = Column(String(20), nullable=True)
```

Note: This User model is exclusively for employees. Clients do not have user accounts in the system and all client interactions are handled as guest transactions.

### 4.2 Booking Model

```python
class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        Index("idx_bookings_date_range", "start_time", "end_time"),
        Index("idx_bookings_status", "status"),
        Index("idx_bookings_phone_normalized", "phone_normalized"),
        Index("idx_bookings_client_phone", "client_phone"),
        Index("idx_bookings_date", "date"),
        Index("idx_bookings_created_at", "created_at"),
        {"extend_existing": True},
    )
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    total_price = Column(Float, nullable=False)
    client_name = Column(String(200), nullable=False)
    client_phone = Column(String(20), nullable=False)
    client_email = Column(String(255), nullable=True)
    phone_normalized = Column(String(20), nullable=True)  # Для оптимизации поиска
    notes = Column(Text, nullable=True)  # Use Text for longer notes
    people_count = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    calendar_event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=True)
    calendar_event = relationship("CalendarEvent", back_populates="bookings")
```

### 4.3 Calendar Event Model

```python
class CalendarEventStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    people_count = Column(Integer, nullable=False)
    status = Column(SAEnum(CalendarEventStatus), nullable=False, default=CalendarEventStatus.pending)
    availability_cached = Column(String(20), nullable=True)
    cache_updated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    bookings = relationship("Booking", back_populates="calendar_event")
```

### 4.4 Client Model (Minimal Data Storage)

```python
class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    email = Column(String(255), nullable=True)
    notes = Column(String(1000), nullable=True)
    preferred_contact_method = Column(String(20), default="phone", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
```

Note: This Client model stores minimal information about clients who make bookings. Clients do not have user accounts or login capabilities. All client interactions are handled as guest transactions without authentication.

### 4.5 Consent and Legal Compliance Models

```python
class UserConsent(Base):
    __tablename__ = "user_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_identifier = Column(String(255), nullable=False)
    consent_type = Column(String(50), nullable=False)
    consent_given = Column(Boolean, nullable=False)
    consent_timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ip_address = Column(INET, nullable=False)
    user_agent = Column(Text, nullable=True)
    consent_version = Column(String(50), nullable=False)
    withdrawal_timestamp = Column(DateTime(timezone=True), nullable=True)
    legal_basis = Column(String(100), nullable=False, default='consent')
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class ComplianceAuditLog(Base):
    __tablename__ = "compliance_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    user_identifier = Column(String(255), nullable=True)
    ip_address = Column(INET, nullable=False)
    user_agent = Column(Text, nullable=True)
    action_details = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    retention_until = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(days=2555), nullable=True)
    document_versions = Column(JSON, nullable=True)
```

## 5. Business Logic Layer

Note: All user accounts in the system are exclusively for employees. Clients do not have user accounts and all client interactions are handled as guest transactions without authentication.

### 5.1 Authentication & Authorization

#### Role-Based Access Control (RBAC)
The system implements a strict RBAC model with the following employee roles:
- **Owner**: Full access to all system features, user management, and business settings
- **Admin**: Full access to system features and user management (except owner-specific functions)
- **Manager**: Access to booking management, calendar, and client interactions
- **Employee**: Basic access to booking management and calendar

Note: Clients do not have user accounts in the system. All bookings by clients are made as guest transactions without authentication.

Access control is implemented at both API route level and within business logic services.

#### Authentication Flow
1. Employee authenticates with username/password
2. System validates credentials and generates JWT access/refresh tokens
3. Tokens are stored securely in HTTP-only cookies
4. Access token is validated on each request
5. Refresh token is used to obtain new access tokens when expired

### 5.2 Booking Management

#### Booking Lifecycle
1. **Pending**: Initial state when booking is created
2. **Confirmed**: Booking is confirmed by employee
3. **Cancelled**: Booking is cancelled by client or employee
4. **Completed**: Booking is marked as completed after service delivery

The booking lifecycle is managed through the `update_booking_status` method in the `BookingService` which ensures proper state transitions and maintains data integrity. This existing functionality will remain unchanged as it is working perfectly.

#### Booking Validation Rules
- Bookings must start and end at full hours (e.g., 10:00-11:00) as validated by the `to_moscow_time` function
- No overlapping bookings for the same time slot with conflict detection
- Client name and phone are required fields with validation
- Only minimal client data is stored (name, phone, and optional email)
- All bookings are stored with Moscow timezone timestamps
- Phone numbers are normalized for efficient searching

### 5.3 Kanban Board Management

#### Board Columns
The Kanban board will have the following default columns:
1. **New Leads**: Newly created bookings requiring attention
2. **Confirmed**: Bookings that have been confirmed
3. **In Progress**: Bookings currently being serviced
4. **Completed**: Successfully completed bookings
5. **Cancelled**: Cancelled bookings

#### Card Operations
- Cards can be moved between columns to reflect booking status
- Each card represents a booking with key information
- Cards can be filtered and sorted by various criteria
- Drag-and-drop interface for intuitive management

### 5.4 Employee Account Lifecycle Management

#### Employee Account States
1. **Active**: Account is active and can be used
2. **Inactive**: Account is deactivated but can be reactivated
3. **Suspended**: Account is temporarily suspended (e.g., for policy violations)
4. **Deleted**: Account is marked for deletion (soft delete)

#### Employee Lifecycle Operations
- **Create**: Only admin/owner can create new employee accounts
- **Activate/Deactivate**: Toggle account active status
- **Suspend**: Temporarily prevent account access
- **Reset Password**: Generate password reset link
- **Delete**: Mark account for deletion (with data retention compliance)

Note: These operations apply only to employee accounts. Clients do not have user accounts in the system.

### 5.5 Legal Compliance

#### Consent Management
- All booking operations require explicit client consent
- Cookie consent is managed through a banner interface
- Consent records are stored with full audit trail
- Users can withdraw consent at any time

#### Data Retention
- Client data is retained for 7 years as required by Russian law
- Audit logs are retained for compliance purposes
- Personal data is securely deleted after retention period

## 6. User Interface Design

### 6.1 Dashboard Overview

The main dashboard will feature:
- Kanban board as the primary interface for booking management
- Quick statistics and metrics
- Recent activity feed
- Calendar integration
- Quick action buttons

### 6.2 Kanban Board Interface

#### Board Layout
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│   New Leads     │   Confirmed     │   In Progress   │   Completed     │   Cancelled     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│                 │                 │                 │                 │                 │
│  [Booking #1]   │  [Booking #2]   │  [Booking #3]   │  [Booking #4]   │  [Booking #5]   │
│  Client: Ivan   │  Client: Maria  │  Client: Alex   │  Client: Elena  │  Client: Peter  │
│  Time: 14:00    │  Time: 16:00    │  Time: 10:00    │  Time: 12:00    │  Time: 15:00    │
│                 │                 │                 │                 │                 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

#### Card Design
Each card will display:
- Client name and contact information
- Booking date and time
- Service type
- Status indicator
- Action buttons (confirm, cancel, complete, etc.)

### 6.3 Responsive Design

The UI will be fully responsive and support:
- Desktop browsers (primary interface)
- Tablet devices
- Mobile devices (limited functionality)

### 6.4 Dark Mode Support

Full dark mode support with automatic detection of system preferences and manual toggle option.

## 7. Security Considerations

### 7.1 Authentication Security

- Password hashing using bcrypt with salt
- JWT tokens with short expiration times
- Refresh token rotation to prevent replay attacks
- Secure HTTP-only cookies for token storage
- Rate limiting on authentication endpoints

### 7.2 Data Security

- All data transmission over HTTPS
- Database encryption for sensitive fields
- Input validation and sanitization
- SQL injection prevention through ORM
- XSS prevention through React's built-in protections

### 7.3 Access Control

- Role-based access control enforced at API level
- Fine-grained permissions for specific operations
- Audit logging of all privileged operations
- Session management with automatic timeout

### 7.4 Legal Compliance

- Full compliance with Russian Federal Law 152-FZ
- Consent management for all data processing activities
- Data retention policies with secure deletion
- Audit trails for all user actions

## 8. Performance Considerations

### 8.1 Database Optimization

- Proper indexing on frequently queried fields
- Connection pooling for database connections
- Query optimization for large dataset operations
- Caching of frequently accessed data

### 8.2 API Performance

- Pagination for large result sets
- Efficient data serialization
- Compression of API responses
- Asynchronous processing for non-critical operations

### 8.3 Frontend Performance

- Code splitting for faster initial loads
- Lazy loading of non-critical components
- Efficient state management with React Query
- Optimized rendering with React.memo and useMemo

## 9. Testing Strategy

### 9.1 Unit Testing

- Backend services with >90% coverage
- Frontend components with >80% coverage
- API endpoint testing
- Business logic validation

### 9.2 Integration Testing

- Database integration tests
- API integration tests
- Third-party service integration tests
- End-to-end workflow testing

### 9.3 Performance Testing

- Load testing with realistic usage patterns
- Stress testing under high load conditions
- Database query performance testing
- Frontend rendering performance testing

## 10. Deployment Considerations

### 10.1 Infrastructure Requirements

- PostgreSQL database (version 13+)
- Python 3.9+ runtime environment
- Node.js 16+ for frontend build
- Docker for containerization
- Reverse proxy (Nginx) for SSL termination

### 10.2 Environment Configuration

- Environment-specific configuration files
- Secure secret management
- Database migration scripts
- Health check endpoints

### 10.3 Monitoring and Logging

- Centralized logging system
- Application performance monitoring
- Database performance monitoring
- Alerting for critical system events

## 11. Migration Plan

### 11.1 Data Migration

1. **User Accounts**: Migrate existing admin users to new role model
2. **Bookings**: Transfer existing booking data to new structure
3. **Calendar Events**: Migrate calendar events with status mapping
4. **Clients**: Migrate client data with minimal data retention

### 11.2 Feature Migration

1. **Phase 1**: Implement new authentication and user management
2. **Phase 2**: Develop Kanban board interface and booking management
3. **Phase 3**: Migrate calendar and availability features
4. **Phase 4**: Implement legal compliance and audit features

### 11.3 Cutover Strategy

- Parallel run of old and new systems during transition
- Gradual migration of users to new interface
- Data synchronization between systems
- Final cutover with minimal downtime

## 12. Development Plan

### 12.1 Phase 1: Foundation (Weeks 1-3)

#### Week 1: Project Setup and Authentication
- Set up development environment
- Implement authentication system with JWT
- Create user management API endpoints
- Develop login/logout UI components

#### Week 2: User Management
- Implement role-based access control
- Develop user management UI
- Create user account lifecycle management
- Implement password reset functionality

#### Week 3: Data Models and API
- Finalize data models for bookings and calendar events
- Implement booking management API
- Implement calendar event management API
- Set up database migrations

### 12.2 Phase 2: Core Functionality (Weeks 4-6)

#### Week 4: Booking Management
- Develop booking creation and editing UI (without modifying existing booking functionality)
- Implement booking status management
- Create booking listing and filtering
- Implement booking validation rules

#### Week 5: Calendar Integration
- Develop calendar view component
- Implement availability management
- Create calendar event management
- Integrate calendar with booking system

#### Week 6: Kanban Board Foundation
- Design Kanban board data structure
- Implement basic Kanban board UI
- Create card components and drag-and-drop functionality
- Integrate Kanban board with booking data

### 12.3 Phase 3: Advanced Features (Weeks 7-9)

#### Week 7: Advanced Kanban Features
- Implement column management
- Add filtering and sorting capabilities
- Create detailed card view and editing
- Implement card movement between columns

#### Week 8: Reporting and Analytics
- Develop dashboard with key metrics
- Create booking statistics and reports
- Implement data visualization components
- Add export functionality

#### Week 9: Legal Compliance
- Implement consent management system
- Create audit logging for all operations
- Develop legal document management
- Ensure compliance with Russian legislation

### 12.4 Phase 4: Testing and Deployment (Weeks 10-12)

#### Week 10: Testing
- Conduct comprehensive unit testing
- Perform integration testing
- Execute performance testing
- Fix identified issues

#### Week 11: User Acceptance Testing
- Conduct user acceptance testing with stakeholders
- Gather feedback and implement improvements
- Perform security testing
- Prepare documentation

#### Week 12: Deployment and Go-Live
- Deploy to production environment
- Monitor system performance
- Provide user training
- Support initial rollout

## 13. Budget Considerations

### 13.1 Development Resources

- All development will use existing team resources
- No additional hiring required for core functionality
- Utilization of existing open-source tools and libraries

### 13.2 Infrastructure Costs

- Hosting on existing infrastructure or budget-friendly cloud providers
- Use of free-tier services where possible
- Self-hosted solutions for databases and services
- Minimal third-party service dependencies

### 13.3 Ongoing Maintenance

- Utilization of existing monitoring and logging infrastructure
- Implementation of automated testing to reduce manual QA costs
- Documentation to reduce onboarding and support costs

## 14. Risk Management

### 14.1 Technical Risks

- **Data Migration Complexity**: Mitigated by thorough testing and rollback plans
- **Performance Issues**: Addressed through performance testing and optimization
- **Integration Challenges**: Managed through modular design and clear interfaces

### 14.2 Compliance Risks

- **Legal Compliance**: Ensured through dedicated compliance features and legal review
- **Data Privacy**: Protected through minimal data storage and encryption

### 14.3 Project Risks

- **Timeline Delays**: Managed through agile methodology and regular progress reviews
- **Scope Creep**: Controlled through clear requirements and change management process

## 15. Quality Assurance

### 15.1 Code Quality Standards

- Adherence to FAANG-level coding standards
- Comprehensive code reviews for all changes
- Automated linting and formatting checks
- Static code analysis tools

### 15.2 Testing Standards

- Minimum 90% code coverage for backend services
- Minimum 80% code coverage for frontend components
- Automated testing in CI/CD pipeline
- Manual testing for critical user flows

### 15.3 Security Standards

- Regular security audits and penetration testing
- Dependency vulnerability scanning
- Secure coding practices training
- Incident response procedures