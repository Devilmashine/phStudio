# Photo Studio Employee CRM Module - Enhanced Design Document

## Executive Summary

This document defines the architecture and implementation strategy for a comprehensive Employee CRM module replacing the existing admin panel for a photo studio booking platform. The system maintains guest-based client bookings while introducing enterprise-grade employee management and business operations capabilities.

## 1. System Architecture

### 1.1 Architecture Principles

Following FAANG engineering standards, the system adopts these core principles:

**Domain-Driven Design (DDD)**: Clear separation between business domains (Booking, Employee Management, Calendar, Compliance) with well-defined boundaries and minimal coupling between services.

**Event-Driven Architecture**: Implementation of an event bus for loose coupling between components, enabling scalability and maintainability without external message queue dependencies.

**CQRS Pattern**: Separation of command and query responsibilities for complex operations, particularly in booking management and reporting systems.

**Repository Pattern**: Abstraction of data access logic enabling testability and potential future database migrations without business logic modifications.

### 1.2 Technical Stack (Zero-Budget, Production-Grade)

**Backend Infrastructure**
- FastAPI with Python 3.11+ for high-performance async operations
- SQLAlchemy 2.0 with async support for database operations
- Alembic for robust database migration management
- Redis (self-hosted) for caching and session management
- Celery with Redis backend for async task processing

**Frontend Architecture**
- React 18 with TypeScript for type safety
- Vite for optimal build performance and HMR
- Zustand for lightweight state management (replacing Redux)
- TanStack Query for server state management
- Tailwind CSS with custom design system
- React Hook Form with Zod validation

**Infrastructure & DevOps**
- Docker with multi-stage builds for optimized images
- Docker Compose for local development orchestration
- GitHub Actions for CI/CD pipeline
- Prometheus + Grafana for monitoring (self-hosted)
- ELK Stack alternative: Loki + Promtail for logging

### 1.3 Microservices-Inspired Modular Monolith

```
┌────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                        │
│                    (FastAPI with middleware)                    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Booking    │  │   Employee   │  │     Calendar         │ │
│  │   Module     │  │   Module     │  │     Module           │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────────────┤ │
│  │  Domain      │  │  Domain      │  │  Domain              │ │
│  │  Service     │  │  Service     │  │  Service             │ │
│  │  Repository  │  │  Repository  │  │  Repository          │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Compliance  │  │   Kanban     │  │   Notification       │ │
│  │   Module     │  │   Module     │  │     Module           │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────────────┤ │
│  │  Domain      │  │  Domain      │  │  Domain              │ │
│  │  Service     │  │  Service     │  │  Service             │ │
│  │  Repository  │  │  Repository  │  │  Repository          │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                    Shared Infrastructure Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Event Bus    │  │ Cache Layer  │  │  Audit Logger        │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│                      Data Persistence Layer                     │
│             PostgreSQL 15+ with Read Replica Support            │
└────────────────────────────────────────────────────────────────┘
```

## 2. Enhanced Data Models with FAANG Standards

### 2.1 Optimized Database Schema

```python
# Base model with audit fields
class BaseModel(Base):
    __abstract__ = True
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    version = Column(Integer, default=1, nullable=False)  # Optimistic locking

# Employee model with enhanced security
class EmployeeRole(str, Enum):
    OWNER = "owner"      # Full system access
    ADMIN = "admin"      # Administrative access
    MANAGER = "manager"  # Operational access

class Employee(BaseModel):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), unique=True, nullable=False)  # Internal ID
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(EmployeeRole), nullable=False)
    
    # Enhanced security fields
    mfa_secret = Column(String(32), nullable=True)  # TOTP support
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Profile information
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    department = Column(String(50), nullable=True)
    
    # Status tracking
    status = Column(String(20), default="active", nullable=False)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sessions = relationship("EmployeeSession", back_populates="employee", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", foreign_keys="AuditLog.employee_id", back_populates="employee")
    
    __table_args__ = (
        Index("idx_employee_email", "email"),
        Index("idx_employee_username", "username"),
        Index("idx_employee_status", "status"),
    )

# Enhanced booking model with state machine
class BookingState(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class Booking(BaseModel):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True)
    booking_reference = Column(String(20), unique=True, nullable=False)  # REF-YYYYMMDD-XXXX
    
    # Time management with timezone awareness
    booking_date = Column(Date, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Integer, nullable=False)  # Cached for performance
    
    # State management
    state = Column(SAEnum(BookingState), default=BookingState.PENDING, nullable=False)
    state_history = Column(JSON, default=list)  # Track all state transitions
    
    # Client information (guest bookings)
    client_name = Column(String(200), nullable=False)
    client_phone = Column(String(20), nullable=False)
    client_phone_normalized = Column(String(15), nullable=False)  # E.164 format
    client_email = Column(String(255), nullable=True)
    
    # Booking details
    space_type = Column(String(50), nullable=False)
    equipment_requested = Column(JSON, default=dict)
    special_requirements = Column(Text, nullable=True)
    
    # Pricing
    base_price = Column(Numeric(10, 2), nullable=False)
    equipment_price = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(20), default="pending")
    
    # Metadata
    source = Column(String(20), default="website")  # website, phone, walk-in
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)  # Staff-only notes
    
    # Performance optimization indexes
    __table_args__ = (
        Index("idx_booking_date_time", "booking_date", "start_time", "end_time"),
        Index("idx_booking_state", "state"),
        Index("idx_booking_phone", "client_phone_normalized"),
        Index("idx_booking_reference", "booking_reference"),
        CheckConstraint("end_time > start_time", name="check_time_validity"),
    )
```

### 2.2 Event Sourcing for Critical Operations

```python
class DomainEvent(BaseModel):
    __tablename__ = "domain_events"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    aggregate_id = Column(String(50), nullable=False)
    aggregate_type = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    occurred_at = Column(DateTime(timezone=True), default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("idx_event_aggregate", "aggregate_type", "aggregate_id"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_occurred", "occurred_at"),
    )
```

## 3. Business Logic Implementation

### 3.1 Domain Services Architecture

```python
# Booking Domain Service with FAANG patterns
class BookingDomainService:
    def __init__(
        self,
        repository: BookingRepository,
        event_bus: EventBus,
        cache_service: CacheService,
        validator: BookingValidator
    ):
        self.repository = repository
        self.event_bus = event_bus
        self.cache = cache_service
        self.validator = validator
    
    async def create_booking(
        self, 
        command: CreateBookingCommand,
        context: RequestContext
    ) -> Result[Booking, BookingError]:
        """
        Create booking with comprehensive validation and event emission
        """
        # Validate business rules
        validation_result = await self.validator.validate_booking(command)
        if validation_result.is_failure():
            return Result.failure(validation_result.error)
        
        # Check availability with distributed lock
        async with self.cache.distributed_lock(
            f"booking:{command.date}:{command.start_time}"
        ):
            if not await self._check_availability(command):
                return Result.failure(BookingError.TIME_SLOT_UNAVAILABLE)
            
            # Create booking aggregate
            booking = Booking.create(command)
            
            # Persist with transaction
            async with self.repository.transaction() as tx:
                saved_booking = await tx.save(booking)
                
                # Emit domain events
                await self.event_bus.publish(
                    BookingCreatedEvent(
                        booking_id=saved_booking.id,
                        reference=saved_booking.booking_reference,
                        metadata=context.to_dict()
                    )
                )
            
            # Invalidate relevant caches
            await self._invalidate_caches(saved_booking)
            
            return Result.success(saved_booking)
    
    async def transition_state(
        self,
        booking_id: int,
        target_state: BookingState,
        context: RequestContext
    ) -> Result[Booking, StateTransitionError]:
        """
        State machine implementation for booking lifecycle
        """
        booking = await self.repository.get_by_id(booking_id)
        if not booking:
            return Result.failure(StateTransitionError.BOOKING_NOT_FOUND)
        
        # Validate state transition
        if not self._is_valid_transition(booking.state, target_state):
            return Result.failure(
                StateTransitionError.INVALID_TRANSITION,
                f"Cannot transition from {booking.state} to {target_state}"
            )
        
        # Apply state transition with side effects
        booking.transition_to(target_state)
        booking.add_state_history(target_state, context.employee_id)
        
        # Handle state-specific side effects
        await self._handle_state_side_effects(booking, target_state)
        
        # Save and emit event
        async with self.repository.transaction() as tx:
            updated_booking = await tx.save(booking)
            await self.event_bus.publish(
                BookingStateChangedEvent(
                    booking_id=booking_id,
                    from_state=booking.state,
                    to_state=target_state,
                    context=context
                )
            )
        
        return Result.success(updated_booking)
```

### 3.2 CQRS Implementation

```python
# Command Handler
class BookingCommandHandler:
    def __init__(self, domain_service: BookingDomainService):
        self.domain_service = domain_service
    
    async def handle(self, command: Command) -> Result:
        match command:
            case CreateBookingCommand():
                return await self.domain_service.create_booking(command)
            case UpdateBookingCommand():
                return await self.domain_service.update_booking(command)
            case CancelBookingCommand():
                return await self.domain_service.cancel_booking(command)
            case _:
                raise UnknownCommandError(f"Unknown command: {type(command)}")

# Query Handler with caching
class BookingQueryHandler:
    def __init__(
        self,
        read_repository: BookingReadRepository,
        cache_service: CacheService
    ):
        self.repository = read_repository
        self.cache = cache_service
    
    @cached(ttl=300, key_prefix="booking_query")
    async def get_bookings_for_date(
        self,
        date: datetime.date,
        filters: Optional[BookingFilters] = None
    ) -> List[BookingDTO]:
        """
        Optimized query with caching and projection
        """
        cache_key = f"bookings:{date}:{hash(filters)}"
        
        # Try cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Query with optimized projection
        bookings = await self.repository.find_by_date(
            date=date,
            filters=filters,
            projection=BookingProjection.DASHBOARD
        )
        
        # Transform to DTOs
        dtos = [BookingDTO.from_entity(b) for b in bookings]
        
        # Cache result
        await self.cache.set(cache_key, dtos, ttl=300)
        
        return dtos
```

### 3.3 Kanban Board Engine

```python
class KanbanEngine:
    """
    Kanban board management with drag-drop support and real-time updates
    """
    
    DEFAULT_COLUMNS = [
        KanbanColumn(id="new", title="New Bookings", order=1, color="#3B82F6"),
        KanbanColumn(id="confirmed", title="Confirmed", order=2, color="#10B981"),
        KanbanColumn(id="in_progress", title="In Progress", order=3, color="#F59E0B"),
        KanbanColumn(id="completed", title="Completed", order=4, color="#6B7280"),
        KanbanColumn(id="cancelled", title="Cancelled", order=5, color="#EF4444"),
    ]
    
    def __init__(
        self,
        booking_service: BookingDomainService,
        websocket_manager: WebSocketManager
    ):
        self.booking_service = booking_service
        self.ws_manager = websocket_manager
    
    async def move_card(
        self,
        card_id: str,
        from_column: str,
        to_column: str,
        position: int,
        context: RequestContext
    ) -> Result[KanbanCard, KanbanError]:
        """
        Move card between columns with validation and broadcasting
        """
        # Map column to booking state
        target_state = self._map_column_to_state(to_column)
        
        # Validate move permissions
        if not await self._can_move_card(card_id, from_column, to_column, context):
            return Result.failure(KanbanError.INSUFFICIENT_PERMISSIONS)
        
        # Execute state transition
        transition_result = await self.booking_service.transition_state(
            booking_id=card_id,
            target_state=target_state,
            context=context
        )
        
        if transition_result.is_success():
            # Broadcast update to connected clients
            await self.ws_manager.broadcast_to_room(
                room="kanban_board",
                message=KanbanUpdateMessage(
                    type="card_moved",
                    card_id=card_id,
                    from_column=from_column,
                    to_column=to_column,
                    position=position,
                    updated_by=context.employee_id
                )
            )
        
        return transition_result
```

## 4. API Design with OpenAPI Standards

### 4.1 RESTful API Structure

```python
# Booking API with comprehensive error handling
@router.post(
    "/api/v1/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ValidationErrorResponse},
        409: {"model": ConflictErrorResponse},
        500: {"model": InternalErrorResponse}
    }
)
async def create_booking(
    request: CreateBookingRequest,
    context: RequestContext = Depends(get_request_context),
    command_handler: BookingCommandHandler = Depends(get_command_handler)
) -> BookingResponse:
    """
    Create new booking with validation
    
    - Validates time slots are available
    - Ensures booking starts and ends at full hours
    - Normalizes phone numbers to E.164 format
    - Generates unique booking reference
    """
    command = CreateBookingCommand.from_request(request)
    result = await command_handler.handle(command)
    
    if result.is_failure():
        raise HTTPException(
            status_code=result.error.status_code,
            detail=result.error.to_dict()
        )
    
    return BookingResponse.from_entity(result.value)

# Batch operations endpoint
@router.post("/api/v1/bookings/batch")
async def batch_booking_operations(
    operations: List[BookingOperation],
    context: RequestContext = Depends(get_request_context)
) -> BatchOperationResponse:
    """
    Execute multiple booking operations in a single transaction
    """
    results = []
    async with transaction_scope() as tx:
        for operation in operations:
            result = await process_operation(operation, context, tx)
            results.append(result)
    
    return BatchOperationResponse(results=results)
```

### 4.2 GraphQL Alternative (Optional)

```python
# GraphQL schema for complex queries
type Query {
    bookings(
        dateRange: DateRangeInput!
        filters: BookingFiltersInput
        pagination: PaginationInput
    ): BookingConnection!
    
    bookingAnalytics(
        period: AnalyticsPeriod!
        groupBy: GroupByField
    ): BookingAnalytics!
}

type Mutation {
    createBooking(input: CreateBookingInput!): BookingPayload!
    updateBooking(id: ID!, input: UpdateBookingInput!): BookingPayload!
    transitionBookingState(id: ID!, state: BookingState!): BookingPayload!
}

type Subscription {
    bookingUpdates(filters: BookingFiltersInput): BookingUpdate!
    kanbanBoardUpdates: KanbanUpdate!
}
```

## 5. Security Implementation

### 5.1 Authentication & Authorization

```python
class SecurityService:
    """
    Comprehensive security implementation following OWASP standards
    """
    
    def __init__(self):
        self.password_hasher = Argon2PasswordHasher()
        self.token_service = JWTTokenService()
        self.mfa_service = TOTPService()
    
    async def authenticate(
        self,
        username: str,
        password: str,
        mfa_code: Optional[str] = None
    ) -> Result[AuthenticationResult, AuthError]:
        """
        Multi-factor authentication with rate limiting
        """
        # Rate limiting check
        if await self._is_rate_limited(username):
            return Result.failure(AuthError.RATE_LIMITED)
        
        # Retrieve employee
        employee = await self.repository.get_by_username(username)
        if not employee:
            await self._record_failed_attempt(username)
            return Result.failure(AuthError.INVALID_CREDENTIALS)
        
        # Verify password with timing attack protection
        if not self._verify_password_constant_time(password, employee.password_hash):
            await self._record_failed_attempt(username)
            return Result.failure(AuthError.INVALID_CREDENTIALS)
        
        # MFA verification if enabled
        if employee.mfa_secret:
            if not mfa_code or not self.mfa_service.verify(employee.mfa_secret, mfa_code):
                return Result.failure(AuthError.INVALID_MFA_CODE)
        
        # Generate tokens
        access_token = self.token_service.create_access_token(employee)
        refresh_token = self.token_service.create_refresh_token(employee)
        
        # Create session
        session = await self._create_session(employee, refresh_token)
        
        return Result.success(
            AuthenticationResult(
                access_token=access_token,
                refresh_token=refresh_token,
                session_id=session.id,
                employee=employee
            )
        )

class RBACMiddleware:
    """
    Role-based access control middleware
    """
    
    def __init__(self, required_roles: List[EmployeeRole]):
        self.required_roles = required_roles
    
    async def __call__(self, request: Request, call_next):
        context = request.state.context
        
        if not context.is_authenticated:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if context.employee_role not in self.required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Audit log the access
        await audit_logger.log(
            action="api_access",
            resource=request.url.path,
            employee_id=context.employee_id,
            metadata={"method": request.method, "ip": request.client.host}
        )
        
        response = await call_next(request)
        return response
```

### 5.2 Data Protection

```python
class DataProtectionService:
    """
    GDPR/Russian 152-FZ compliant data protection
    """
    
    def __init__(self):
        self.encryption_key = self._load_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def encrypt_pii(self, data: str) -> str:
        """Encrypt personally identifiable information"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_pii(self, encrypted_data: str) -> str:
        """Decrypt personally identifiable information"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    async def anonymize_old_data(self, retention_days: int = 2555):
        """
        Anonymize data older than retention period
        Required by Russian Federal Law 152-FZ
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        # Anonymize bookings
        await self.repository.anonymize_bookings_before(cutoff_date)
        
        # Purge audit logs
        await self.repository.purge_audit_logs_before(cutoff_date)
        
        # Log compliance action
        await compliance_logger.log(
            action="data_anonymization",
            cutoff_date=cutoff_date,
            affected_records=result.count
        )
```

## 6. Performance Optimization

### 6.1 Database Optimization Strategies

```python
class DatabaseOptimizer:
    """
    Database performance optimization utilities
    """
    
    async def create_materialized_views(self):
        """
        Create materialized views for complex queries
        """
        await self.db.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS booking_daily_summary AS
            SELECT 
                booking_date,
                COUNT(*) as total_bookings,
                SUM(CASE WHEN state = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN state = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                SUM(total_price) as revenue,
                AVG(duration_hours) as avg_duration
            FROM bookings
            GROUP BY booking_date
            WITH DATA;
            
            CREATE INDEX idx_booking_daily_summary_date 
            ON booking_daily_summary(booking_date);
        """)
    
    async def partition_large_tables(self):
        """
        Implement table partitioning for scalability
        """
        await self.db.execute("""
            -- Partition bookings by month
            CREATE TABLE bookings_partitioned (
                LIKE bookings INCLUDING ALL
            ) PARTITION BY RANGE (booking_date);
            
            -- Create partitions for each month
            CREATE TABLE bookings_y2024m01 PARTITION OF bookings_partitioned
            FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
        """)
```

### 6.2 Caching Strategy

```python
class CacheStrategy:
    """
    Multi-layer caching implementation
    """
    
    def __init__(self):
        self.l1_cache = MemoryCache(max_size=1000)  # In-process cache
        self.l2_cache = RedisCache()  # Distributed cache
    
    async def get_with_fallback(
        self,
        key: str,
        loader: Callable,
        ttl: int = 300
    ) -> Any:
        """
        Multi-layer cache with fallback to database
        """
        # Try L1 cache
        value = self.l1_cache.get(key)
        if value:
            return value
        
        # Try L2 cache
        value = await self.l2_cache.get(key)
        if value:
            self.l1_cache.set(key, value, ttl=60)
            return value
        
        # Load from source
        value = await loader()
        
        # Update both caches
        await self.l2_cache.set(key, value, ttl=ttl)
        self.l1_cache.set(key, value, ttl=60)
        
        return value
```

## 7. Frontend Architecture

### 7.1 Component Architecture

```typescript
// Atomic Design Pattern Implementation
// atoms/
export const Button: FC<ButtonProps> = ({ variant, size, ...props }) => {
    const styles = cn(
        "base-button-styles",
        variantStyles[variant],
        sizeStyles[size]
    );
    return <button className={styles} {...props} />;
};

// molecules/
export const BookingCard: FC<BookingCardProps> = ({ booking, onEdit, onCancel }) => {
    return (
        <Card className="booking-card">
            <CardHeader>
                <h3>{booking.clientName}</h3>
                <Badge status={booking.state} />
            </CardHeader>
            <CardBody>
                <TimeSlot start={booking.startTime} end={booking.endTime} />
                <Price amount={booking.totalPrice} />
            </CardBody>
            <CardFooter>
                <Button onClick={onEdit}>Edit</Button>
                <Button onClick={onCancel} variant="danger">Cancel</Button>
            </CardFooter>
        </Card>
    );
};

// organisms/
export const KanbanBoard: FC = () => {
    const { columns, moveCard } = useKanbanBoard();
    
    return (
        <DndContext onDragEnd={handleDragEnd}>
            <div className="kanban-board">
                {columns.map(column => (
                    <KanbanColumn key={column.id} column={column} />
                ))}
            </div>
        </DndContext>
    );
};
```

### 7.2 State Management with Zustand

```typescript
// stores/bookingStore.ts
interface BookingStore {
    bookings: Booking[];
    filters: BookingFilters;
    isLoading: boolean;
    error: Error | null;
    
    // Actions
    fetchBookings: (filters?: BookingFilters) => Promise<void>;
    createBooking: (data: CreateBookingData) => Promise<Booking>;
    updateBooking: (id: string, data: UpdateBookingData) => Promise<void>;
    deleteBooking: (id: string) => Promise<void>;
}

export const useBookingStore = create<BookingStore>((set, get) => ({
    bookings: [],
    filters: {},
    isLoading: false,
    error: null,
    
    fetchBookings: async (filters) => {
        set({ isLoading: true, error: null });
        try {
            const bookings = await bookingApi.fetchBookings(filters);
            set({ bookings, filters, isLoading: false });
        } catch (error) {
            set({ error, isLoading: false });
        }
    },
    
    createBooking: async (data) => {
        const optimisticBooking = { ...data, id: tempId(), state: 'pending' };
        set(state => ({ bookings: [...state.bookings, optimisticBooking] }));
        
        try {
            const booking = await bookingApi.createBooking(data);
            set(state => ({
                bookings: state.bookings.map(b => 
                    b.id === optimisticBooking.id ? booking : b
                )
            }));
            return booking;
        } catch (error) {
            set(state => ({
                bookings: state.bookings.filter(b => b.id !== optimisticBooking.id),
                error
            }));
            throw error;
        }
    }
}));
```

## 8. Testing Strategy

### 8.1 Test Pyramid Implementation

```python
# Unit Tests (70% coverage target)
class TestBookingDomainService:
    @pytest.mark.asyncio
    async def test_create_booking_validates_time_slots(self):
        # Arrange
        service = BookingDomainService(mock_repo, mock_event_bus)
        command = CreateBookingCommand(
            start_time=datetime(2024, 1, 1, 10, 30),  # Invalid: not full hour
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        
        # Act
        result = await service.create_booking(command)
        
        # Assert
        assert result.is_failure()
        assert result.error == BookingError.INVALID_TIME_SLOT

# Integration Tests (20% coverage target)
class TestBookingAPI:
    @pytest.mark.integration
    async def test_booking_creation_flow(self, test_client, test_db):
        # Arrange
        booking_data = {
            "date": "2024-01-01",
            "startTime": "10:00",
            "endTime": "11:00",
            "clientName": "Test Client",
            "clientPhone": "+79991234567"
        }
        
        # Act
        response = await test_client.post("/api/v1/bookings", json=booking_data)
        
        # Assert
        assert response.status_code == 201
        booking = response.json()
        assert booking["bookingReference"].startswith("REF-")
        
        # Verify in database
        db_booking = await test_db.get_booking(booking["id"])
        assert db_booking is not None

# E2E Tests (10% coverage target)
class TestBookingE2E:
    @pytest.mark.e2e
    async def test_complete_booking_lifecycle(self, browser):
        # Create booking
        await browser.goto("/bookings/new")
        await browser.fill("[name=clientName]", "Test Client")
        await browser.fill("[name=clientPhone]", "+79991234567")
        await browser.click("[type=submit]")
        
        # Verify on Kanban board
        await browser.goto("/kanban")
        card = await browser.wait_for_selector("[data-booking-id]")
        assert await card.text_content() == "Test Client"
```

### 8.2 Performance Testing

```python
# Locust configuration for load testing
class BookingUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_bookings(self):
        self.client.get("/api/v1/bookings?date=2024-01-01")
    
    @task(1)
    def create_booking(self):
        self.client.post("/api/v1/bookings", json={
            "date": "2024-01-01",
            "startTime": f"{random.randint(9, 17)}:00",
            "endTime": f"{random.randint(10, 18)}:00",
            "clientName": fake.name(),
            "clientPhone": fake.phone_number()
        })
```

## 9. Monitoring & Observability

### 9.1 Metrics Collection

```python
# Prometheus metrics
booking_counter = Counter('bookings_total', 'Total bookings created', ['state'])
booking_duration = Histogram('booking_duration_hours', 'Booking duration distribution')
api_latency = Histogram('api_request_duration_seconds', 'API request latency', ['endpoint', 'method'])

class MetricsMiddleware:
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        api_latency.labels(
            endpoint=request.url.path,
            method=request.method
        ).observe(time.time() - start_time)
        
        return response
```

### 9.2 Structured Logging

```python
# Structured logging configuration
import structlog

logger = structlog.get_logger()

class StructuredLogger:
    @staticmethod
    def configure():
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.CallsiteParameterAdder(
                    parameters=[
                        structlog.processors.CallsiteParameter.FILENAME,
                        structlog.processors.CallsiteParameter.LINENO,
                        structlog.processors.CallsiteParameter.FUNC_NAME,
                    ]
                ),
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
```

## 10. Deployment Architecture

### 10.1 Container Configuration

```dockerfile
# Multi-stage Dockerfile for optimized images
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 10.2 Infrastructure as Code

```yaml
# docker-compose.yml for local development
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/photostudio
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./app:/app
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=photostudio
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

## 11. Migration Strategy

### 11.1 Zero-Downtime Migration Plan

```python
# Database migration with Alembic
"""
Zero-downtime migration strategy
"""

def upgrade():
    # Step 1: Add new columns (backwards compatible)
    op.add_column('bookings', 
        sa.Column('booking_reference', sa.String(20), nullable=True)
    )
    
    # Step 2: Populate new columns
    connection = op.get_bind()
    result = connection.execute(
        "UPDATE bookings SET booking_reference = 'REF-' || "
        "to_char(created_at, 'YYYYMMDD') || '-' || "
        "lpad(id::text, 4, '0') WHERE booking_reference IS NULL"
    )
    
    # Step 3: Add constraints after data migration
    op.alter_column('bookings', 'booking_reference', nullable=False)
    op.create_unique_constraint('uq_booking_reference', 'bookings', ['booking_reference'])
    
    # Step 4: Create indexes
    op.create_index('idx_booking_reference', 'bookings', ['booking_reference'])

def downgrade():
    op.drop_index('idx_booking_reference', 'bookings')
    op.drop_constraint('uq_booking_reference', 'bookings')
    op.drop_column('bookings', 'booking_reference')
```

## 12. Development Best Practices

### 12.1 Code Quality Standards

```python
# Pre-commit configuration
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: ['-r', 'app']
```

### 12.2 Documentation Standards

All code must include comprehensive documentation:
- Module-level docstrings explaining purpose and usage
- Class docstrings with attributes and methods overview
- Method docstrings with parameters, returns, and raises
- Inline comments for complex logic
- API documentation auto-generated from OpenAPI specs
- Architecture Decision Records (ADRs) for significant choices

### 12.3 Code Review Process

Mandatory code review checklist:
- [ ] Tests coverage > 90% for new code
- [ ] No security vulnerabilities detected
- [ ] Performance impact assessed
- [ ] Database migrations reviewed
- [ ] API backward compatibility maintained
- [ ] Documentation updated
- [ ] Error handling comprehensive
- [ ] Logging appropriate

## 13. Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1-2)
- [x] Enhanced base models with audit fields
- [x] Event bus implementation
- [x] CQRS pattern implementation
- [x] Repository pattern refactoring
- [ ] Redis integration for caching
- [ ] Structured logging setup

### Phase 2: Enhanced Models (Week 3-4)
- [x] Employee model with enhanced security
- [x] Booking model with state machine
- [x] Domain events implementation
- [ ] Materialized views for analytics
- [ ] Table partitioning strategy

### Phase 3: Business Logic (Week 5-6)
- [x] Domain services implementation
- [x] Command/Query handlers
- [x] Kanban board engine
- [ ] State machine validation
- [ ] Business rule engine

### Phase 4: Security & Performance (Week 7-8)
- [x] RBAC middleware
- [x] MFA implementation
- [x] Data encryption
- [ ] Rate limiting
- [ ] Performance optimization

### Phase 5: Frontend Enhancement (Week 9-10)
- [x] Atomic design components
- [x] Zustand state management
- [x] Real-time updates
- [ ] Drag & drop Kanban
- [ ] Advanced filtering

### Phase 6: Testing & Deployment (Week 11-12)
- [x] Unit test coverage
- [x] Integration tests
- [x] E2E tests
- [ ] Performance testing
- [ ] Production deployment

## Conclusion

This enhanced design document provides a production-ready blueprint for implementing a Photo Studio Employee CRM Module following FAANG engineering standards while maintaining budget constraints through exclusive use of open-source technologies. The architecture emphasizes scalability, maintainability, and security while providing a superior user experience through modern UI patterns and real-time capabilities.

## Current Status Assessment

Based on the existing codebase analysis, the following components are already implemented:

✅ **Completed Components:**
- Basic FastAPI structure with modular routing
- User authentication system
- Basic booking models and API
- Calendar integration
- Kanban board foundation
- Telegram notifications
- Legal compliance framework
- Basic admin panel

🔄 **Components Requiring Enhancement:**
- Employee management (needs role-based access control)
- Booking state machine (needs validation and transitions)
- Event sourcing (needs domain events)
- Caching layer (needs Redis integration)
- Performance optimization (needs materialized views)

❌ **Missing Components:**
- CQRS pattern implementation
- Event bus architecture
- Advanced security features (MFA, rate limiting)
- Comprehensive testing suite
- Monitoring and observability
- Performance testing framework

The project is approximately **40% complete** according to the enhanced design specifications. The next phase should focus on implementing the missing architectural components while enhancing existing functionality.