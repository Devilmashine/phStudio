# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a comprehensive Photo Studio Employee CRM Module built as a modular monolith following FAANG engineering standards. The system replaces a basic admin panel with enterprise-grade employee management and business operations capabilities while maintaining guest-based client bookings.

## Architecture Principles

- **Domain-Driven Design (DDD)**: Clear separation between business domains (Booking, Employee Management, Calendar, Compliance)
- **Event-Driven Architecture**: Event bus for loose coupling between components
- **CQRS Pattern**: Separation of command and query responsibilities
- **Repository Pattern**: Abstraction of data access logic for testability

## Tech Stack

### Backend
- **API**: FastAPI with Python 3.11+ for high-performance async operations
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0 async support
- **Caching**: Redis for caching and session management
- **Tasks**: Celery with Redis backend for async processing
- **Migrations**: Alembic for database migration management

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for optimal build performance
- **State Management**: Zustand for lightweight state management
- **Server State**: TanStack Query for server state management
- **Styling**: Tailwind CSS with custom design system
- **Forms**: React Hook Form with Zod validation

## Development Commands

### Client Application
Navigate to the client directory first:
```bash
cd /Users/devilmashine/photo-studio-booking/client
```

**Development Commands:**
- `npm start` - Start development server on http://localhost:3000
- `npm run build` - Build for production (outputs to `build/` directory)
- `npm test` - Run tests in interactive watch mode
- `npm run eject` - Eject from Create React App (one-way operation)

**Testing Commands:**
- `npm test -- --watchAll=false` - Run all tests once without watch mode
- `npm test -- --coverage` - Run tests with coverage report
- `npm test -- ComponentName.test` - Run specific test file

### Backend API
```bash
# Start development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests with coverage
pytest --cov=app tests/

# Run specific test module
pytest tests/test_booking_service.py -v

# Format code
black app tests

# Lint code
flake8 app tests

# Type checking
mypy app
```

### Docker Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Run migrations in container
docker-compose exec app alembic upgrade head

# Run tests in container
docker-compose exec app pytest

# Access database
docker-compose exec postgres psql -U user -d photostudio
```

## System Architecture

### Modular Monolith Structure
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

### Frontend Project Structure
```
client/src/
├── components/         # Reusable UI components (Atomic Design)
│   ├── atoms/          # Basic building blocks (Button, Input)
│   ├── molecules/      # Simple combinations (BookingCard, SearchBar)
│   └── organisms/      # Complex components (KanbanBoard, Calendar)
├── pages/             # Route-specific page components
│   ├── HomePage.tsx   # Landing/home page
│   ├── StudiosPage.tsx # Studio listing and search
│   ├── BookingPage.tsx # Studio booking form
│   ├── AuthPage.tsx   # Login/registration
│   └── ProfilePage.tsx # User profile/dashboard
├── stores/            # Zustand state management
│   ├── bookingStore.ts # Booking state and actions
│   └── authStore.ts   # Authentication state
├── hooks/             # Custom React hooks
├── services/          # API integration layer
├── types/             # TypeScript type definitions
│   └── index.ts       # Shared interfaces (User, Booking, etc.)
├── App.tsx           # Main app component with routing
└── index.tsx         # App entry point
```

### Backend Project Structure
```
app/
├── api/               # FastAPI route handlers
│   ├── v1/           # API version 1 routes
│   └── dependencies.py # Shared dependencies
├── core/              # Core application configuration
│   ├── config.py     # Application settings
│   ├── security.py   # Authentication & authorization
│   └── database.py   # Database configuration
├── domains/           # Domain modules (DDD)
│   ├── booking/      # Booking domain
│   │   ├── models.py # Domain models
│   │   ├── services.py # Business logic
│   │   ├── repository.py # Data access
│   │   └── events.py # Domain events
│   ├── employee/     # Employee domain
│   └── calendar/     # Calendar domain
├── shared/           # Shared infrastructure
│   ├── event_bus.py  # Event handling
│   ├── cache.py      # Caching layer
│   └── audit.py      # Audit logging
├── migrations/       # Alembic database migrations
└── tests/            # Test suite
    ├── unit/         # Unit tests
    ├── integration/  # Integration tests
    └── e2e/          # End-to-end tests
```

### Routing Configuration
The application uses React Router with these main routes:
- `/` - HomePage (landing page with studio previews)
- `/studios` - StudiosPage (full studio listing with search)
- `/booking/:studioId` - BookingPage (booking form for specific studio)
- `/auth` - AuthPage (authentication forms)
- `/profile` - ProfilePage (user dashboard)

### State Management
- **Authentication**: Currently mock implementation in App.tsx (lines 60-69)
- **No centralized state management**: Uses local component state with useState
- **Props drilling**: User/auth state passed from App.tsx to Navbar

### UI/UX Patterns
- **Theme**: Custom MUI theme with primary color #2c3e50, secondary #f39c12
- **Typography**: Inter font family with custom font weights
- **Components**: Rounded corners (borderRadius: 8-12px), custom shadows
- **Responsive**: Grid system using MUI's GridLegacy component
- **Navigation**: Top navbar with conditional rendering based on auth status

### API Integration
- **HTTP Client**: Axios configured as dependency
- **Current State**: No actual API calls implemented - using mock data
- **Mock Data**: Studios array hardcoded in HomePage.tsx and StudiosPage.tsx

## Development Workflow

### Key Files to Understand
1. **App.tsx** - Main routing, theme configuration, and auth state
2. **components/Navbar.tsx** - Navigation logic and user menu
3. **pages/HomePage.tsx** - Landing page with feature showcase
4. **pages/StudiosPage.tsx** - Studio listing with search interface
5. **types/index.ts** - Shared TypeScript interfaces

### Common Development Tasks

**Adding a new page:**
1. Create component in `src/pages/`
2. Add route in `App.tsx` Routes configuration
3. Add navigation link in `Navbar.tsx` if needed

**Adding new components:**
1. Create in `src/components/`
2. Follow existing MUI styling patterns
3. Import and use TypeScript interfaces from `src/types/`

**Styling conventions:**
- Use MUI's `sx` prop for component styling
- Follow existing theme structure (primary, secondary colors)
- Maintain consistent spacing (py, px, mb, etc.)
- Use hover effects with `transform: translateY(-4px)`

## Core Development Patterns

### Domain-Driven Design (DDD)
- Each domain module (booking, employee, calendar) is self-contained
- Domain services contain business logic
- Repositories abstract data access
- Domain events enable loose coupling between modules

### CQRS Implementation
- Commands handle write operations with validation
- Queries handle read operations with caching
- Separate command and query handlers for complex operations
- Event sourcing for critical business operations

### Event-Driven Architecture
- Domain events published on state changes
- Event handlers process side effects asynchronously
- Event bus coordinates communication between domains
- No external message queue dependencies (Redis-based)

### State Machine Pattern
- Booking lifecycle managed through state transitions
- Valid state transitions enforced at domain level
- State history tracked for audit purposes
- Kanban board reflects booking states in real-time

## Development Best Practices

### Code Quality Standards
```bash
# Pre-commit hooks automatically run:
black .           # Code formatting
flake8 .          # Linting
mypy .            # Type checking
bandit app/       # Security scanning
pytest --cov=90   # Test coverage enforcement
```

### Testing Strategy (Test Pyramid)
- **Unit Tests (70%)**: Fast, isolated tests for business logic
- **Integration Tests (20%)**: Database and API integration
- **E2E Tests (10%)**: Complete user workflows

### Database Migrations
```bash
# Create migration after model changes
alembic revision --autogenerate -m "add booking reference field"

# Review generated migration before applying
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Security Implementation
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: PII encryption, audit logging
- **Rate Limiting**: Per-user and per-endpoint limits
- **Input Validation**: Pydantic models with custom validators

### Performance Optimization
- **Database**: Materialized views, partitioning, proper indexing
- **Caching**: Multi-layer (in-memory + Redis) with cache invalidation
- **API**: Background tasks with Celery for heavy operations
- **Frontend**: Code splitting, lazy loading, optimistic updates

## Current Implementation Status

### Frontend (Client)
- **Status**: Basic React app with Material-UI
- **Authentication**: Mock implementation in App.tsx (lines 60-69)
- **State Management**: Local component state (needs Zustand integration)
- **Data**: Hardcoded studio arrays in HomePage/StudiosPage
- **Next Steps**: Integrate with backend API, implement real auth

### Backend API
- **Status**: Architecture defined, implementation needed
- **Database**: PostgreSQL schema designed
- **Domains**: Booking, Employee, Calendar modules to implement
- **Infrastructure**: Event bus, caching, audit logging to build

## TypeScript Configuration
- Strict mode enabled for both frontend and backend
- Path mapping configured for clean imports
- Shared types between frontend/backend through API contracts
- Zod for runtime validation and type inference
