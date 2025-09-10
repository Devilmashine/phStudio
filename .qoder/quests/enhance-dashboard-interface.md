# Photo Studio Employee CRM Module - Enhanced Dashboard Interface Design

## 1. System Architecture

### 1.1 Architecture Principles

Following FAANG engineering standards, the system adopts these core principles:

**Domain-Driven Design (DDD)**: Clear separation between business domains (Booking, Employee Management, Calendar, Compliance) with well-defined boundaries and minimal coupling between services.

**Event-Driven Architecture**: Implementation of an event bus for loose coupling between components, enabling scalability and maintainability without external message queue dependencies.

**CQRS Pattern**: Separation of command and query responsibilities for complex operations, particularly in booking management and reporting systems.

**Repository Pattern**: Abstraction of data access logic enabling testability and potential future database migrations without business logic modifications.

### 1.2 Technical Stack (Zero-Budget, Production-Grade)

**Frontend Architecture**
- React 19 with TypeScript for type safety
- Vite for optimal build performance and HMR
- Zustand for lightweight state management (replacing Redux)
- TanStack Query for server state management
- Tailwind CSS with custom design system
- React Hook Form with Zod validation
- Chart.js for data visualization

## 2. Enhanced Dashboard Interface Design

### 2.1 Dashboard Layout and Structure

The enhanced dashboard will follow a responsive grid layout with the following components:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Dashboard Header                                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ Date Range   │ │ Refresh      │ │ Export       │ │ Settings     │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Key Metrics Summary (Scrollable Cards)                             │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                │    │
│  │  │ Total    │ │ Revenue  │ │ Clients  │ │ Canceled │                │    │
│  │  │ Bookings │ │          │ │          │ │          │                │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────┬──────────────────────────────────────┐    │
│  │  Booking List (Scrollable)   │  Calendar View                       │    │
│  │  ┌───────────────────────┐   │  ┌───────────────────────────────┐   │    │
│  │  │ Filter/Search         │   │  │ Date Selection                │   │    │
│  │  ├───────────────────────┤   │  ├───────────────────────────────┤   │    │
│  │  │ Booking 1             │   │  │ Calendar Component            │   │    │
│  │  │ Booking 2             │   │  │                               │   │    │
│  │  │ Booking 3             │   │  │                               │   │    │
│  │  │ ...                   │   │  │                               │   │    │
│  │  │ Booking N             │   │  │                               │   │    │
│  │  └───────────────────────┘   │  └───────────────────────────────┘   │    │
│  └──────────────────────────────┴──────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Data Visualization (Interactive Charts)                            │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │                                                             │    │    │
│  │  │  [Line Chart] Bookings Over Time                            │    │    │
│  │  │                                                             │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │  ┌─────────────────┬─────────────────┬─────────────────────────┐    │    │
│  │  │ [Bar Chart]     │ [Pie Chart]     │ [Heatmap]               │    │    │
│  │  │ Bookings by Day │ Booking Status  │ Peak Hours              │    │    │
│  │  │ of Week         │ Distribution    │                         │    │    │
│  │  └─────────────────┴─────────────────┴─────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1.1 Responsive Design Implementation

The dashboard layout will adapt to different screen sizes using CSS Grid and Flexbox:

```typescript
const DashboardLayout: React.FC = () => {
  return (
    <div className="dashboard-container">
      {/* Header section */}
      <header className="dashboard-header">
        <div className="header-controls">
          <DateRangeSelector />
          <div className="action-buttons">
            <RefreshButton />
            <ExportButton />
            <SettingsButton />
          </div>
        </div>
      </header>
      
      {/* Main content grid */}
      <main className="dashboard-grid">
        {/* Key metrics - full width on mobile, 4 columns on desktop */}
        <section className="metrics-section">
          <div className="metrics-grid">
            <MetricCard title="Всего бронирований" value="142" change="+12%" />
            <MetricCard title="Доход" value="₽245,600" change="+8%" />
            <MetricCard title="Клиенты" value="86" change="+3%" />
            <MetricCard title="Отказы" value="12" change="-2%" />
          </div>
        </section>
        
        {/* Booking list and calendar - stacked on mobile, side-by-side on desktop */}
        <section className="content-section">
          <div className="content-grid">
            <div className="booking-list-container">
              <BookingList />
            </div>
            <div className="calendar-container">
              <CalendarComponent />
            </div>
          </div>
        </section>
        
        {/* Charts section - full width */}
        <section className="charts-section">
          <div className="charts-grid">
            <div className="chart-container">
              <BookingsOverTimeChart />
            </div>
            <div className="chart-row">
              <div className="chart-container">
                <BookingsByDayChart />
              </div>
              <div className="chart-container">
                <BookingStatusChart />
              </div>
              <div className="chart-container">
                <PeakHoursHeatmap />
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};
```

```css
/* Responsive CSS for dashboard layout */
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
}

.dashboard-header {
  margin-bottom: 1rem;
}

.header-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .header-controls {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.dashboard-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-rows: auto 1fr auto;
}

.metrics-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .metrics-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.content-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 1024px) {
  .content-grid {
    grid-template-columns: 2fr 1fr;
  }
}

.charts-grid {
  display: grid;
  gap: 1rem;
}

.chart-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1rem;
}

.chart-row {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .chart-row {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 2.2 Component Specifications

#### 2.2.1 Scrollable Booking List Component

**Requirements:**
- Vertical scrolling for large datasets with virtualization
- Pagination implementation for better performance
- Filtering capabilities (by date, status, client name)
- Sorting by any column
- Interactive row actions (edit, cancel, view details)
- Real-time updates via WebSocket
- Responsive design for all screen sizes

**Implementation Details:**
```typescript
interface BookingListItem {
  id: number;
  reference: string;
  clientName: string;
  date: string;
  startTime: string;
  endTime: string;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  totalPrice: number;
  serviceName: string;
  employeeName?: string;
}

interface BookingListProps {
  bookings: BookingListItem[];
  onBookingSelect: (bookingId: number) => void;
  onStatusChange: (bookingId: number, newStatus: string) => void;
  loading: boolean;
  error: string | null;
  totalCount: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  filters: BookingFilters;
  onFiltersChange: (filters: BookingFilters) => void;
}

const BookingList: React.FC<BookingListProps> = ({
  bookings,
  onBookingSelect,
  onStatusChange,
  loading,
  error,
  totalCount,
  currentPage,
  onPageChange,
  filters,
  onFiltersChange
}) => {
  // Implementation with virtualized scrolling for performance
  // Filtering and sorting state management
  // Responsive design for all screen sizes
  // Interactive elements with hover effects and click handlers
  // Expandable rows for detailed information
}
```

#### 2.2.2 Interactive Calendar Component

**Requirements:**
- Month view with availability indicators
- Click to select date for detailed view
- Color-coded status indicators
- Real-time updates
- Responsive design
- Tooltip information on hover
- Current day highlighting

**Implementation Details:**
```typescript
interface CalendarDay {
  date: Date;
  status: 'available' | 'partially_booked' | 'fully_booked' | 'past';
  availableSlots: number;
  totalSlots: number;
  bookings: number; // Number of bookings for this day
}

interface CalendarProps {
  selectedDate: Date | null;
  onDateSelect: (date: Date) => void;
  availabilityData: Record<string, CalendarDay>;
  loading: boolean;
  currentDate: Date;
  onMonthChange: (date: Date) => void;
}

const Calendar: React.FC<CalendarProps> = ({
  selectedDate,
  onDateSelect,
  availabilityData,
  loading,
  currentDate,
  onMonthChange
}) => {
  // Implementation with date-fns for date manipulation
  // Custom rendering for each day with status indicators
  // Responsive design for all screen sizes
  
  const getDayClass = (day: CalendarDay) => {
    let baseClass = "flex items-center justify-center h-10 w-10 rounded-full ";
    
    if (isSameDay(day.date, new Date())) {
      baseClass += "bg-blue-500 text-white ";
    } else if (selectedDate && isSameDay(day.date, selectedDate)) {
      baseClass += "bg-indigo-100 text-indigo-800 border-2 border-indigo-500 ";
    }
    
    switch (day.status) {
      case 'available':
        baseClass += "bg-green-100 text-green-800 hover:bg-green-200 cursor-pointer";
        break;
      case 'partially_booked':
        baseClass += "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 cursor-pointer";
        break;
      case 'fully_booked':
        baseClass += "bg-red-100 text-red-800 cursor-not-allowed opacity-50";
        break;
      case 'past':
        baseClass += "bg-gray-100 text-gray-400 cursor-not-allowed";
        break;
      default:
        baseClass += "hover:bg-gray-100 cursor-pointer";
    }
    
    return baseClass;
  };
  
  const renderDay = (day: CalendarDay) => {
    if (!day) {
      return <div className="h-10 w-10" />;
    }
    
    return (
      <div 
        className={getDayClass(day)}
        onClick={() => day.status !== 'past' && day.status !== 'fully_booked' && onDateSelect(day.date)}
        title={`${format(day.date, 'PPP', { locale: ru })}: ${day.bookings} бронирований, ${day.availableSlots} из ${day.totalSlots} слотов свободно`}
      >
        {format(day.date, 'd')}
        {day.bookings > 0 && (
          <div className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-indigo-500"></div>
        )}
      </div>
    );
  };
  
  // Generate calendar grid
  const generateCalendarDays = () => {
    // Implementation to generate calendar days with proper padding
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          {format(currentDate, 'LLLL yyyy', { locale: ru })}
        </h3>
        <div className="flex space-x-2">
          <button 
            onClick={() => onMonthChange(subMonths(currentDate, 1))}
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <ChevronLeftIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
          </button>
          <button 
            onClick={() => onMonthChange(addMonths(currentDate, 1))}
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <ChevronRightIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-7 gap-1 mb-2">
        {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map((day) => (
          <div key={day} className="text-center text-sm font-medium text-gray-500 dark:text-gray-400 py-2">
            {day}
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-7 gap-1">
        {generateCalendarDays().map((day, index) => (
          <div key={index} className="relative flex justify-center">
            {renderDay(day)}
          </div>
        ))}
      </div>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-6 justify-center">
        <div className="flex items-center">
          <div className="w-4 h-4 bg-green-100 border border-green-400 rounded mr-2"></div>
          <span className="text-sm text-gray-600 dark:text-gray-300">Доступно</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-yellow-100 border border-yellow-400 rounded mr-2"></div>
          <span className="text-sm text-gray-600 dark:text-gray-300">Частично занято</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-red-100 border border-red-400 rounded mr-2"></div>
          <span className="text-sm text-gray-600 dark:text-gray-300">Полностью занято</span>
        </div>
      </div>
    </div>
  );
}
```

#### 2.2.3 Interactive Data Visualization Components

**Requirements:**
- Interactive charts with tooltips
- Responsive design that adapts to container size
- Multiple chart types (line, bar, pie, heatmap)
- Loading states and error handling
- Export functionality for charts
- Real-time updates when data changes

**Chart Implementations:**

1. **Bookings Over Time (Line Chart)**
   - X-axis: Dates
   - Y-axis: Number of bookings
   - Interactive tooltips showing exact values
   - Ability to filter by booking status
   - Multiple lines for different booking statuses

```typescript
interface BookingsOverTimeChartProps {
  data: { date: string; count: number; status: string }[];
  loading: boolean;
  onFilterChange: (filters: ChartFilters) => void;
}

const BookingsOverTimeChart: React.FC<BookingsOverTimeChartProps> = ({ 
  data, 
  loading,
  onFilterChange
}) => {
  const chartRef = useRef<ChartJS | null>(null);
  const chartContainerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!chartContainerRef.current || loading) return;
    
    const ctx = chartContainerRef.current.getContext('2d');
    if (!ctx) return;
    
    // Transform data for Chart.js
    const chartData = {
      labels: [...new Set(data.map(d => d.date))],
      datasets: [
        {
          label: 'Подтверждено',
          data: data.filter(d => d.status === 'confirmed').map(d => d.count),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        },
        {
          label: 'Ожидает',
          data: data.filter(d => d.status === 'pending').map(d => d.count),
          borderColor: 'rgb(255, 205, 86)',
          backgroundColor: 'rgba(255, 205, 86, 0.2)',
          tension: 0.1
        },
        // Additional status datasets
      ]
    };
    
    chartRef.current = new Chart(ctx, {
      type: 'line',
      data: chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top' as const,
          },
          title: {
            display: true,
            text: 'Бронирования по датам'
          },
          tooltip: {
            mode: 'index' as const,
            intersect: false,
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Количество бронирований'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Дата'
            }
          }
        },
        interaction: {
          mode: 'nearest' as const,
          axis: 'x' as const,
          intersect: false
        }
      },
    });
    
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [data, loading]);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }
  
  return (
    <div className="relative h-64">
      <canvas ref={chartContainerRef} />
    </div>
  );
};
```

2. **Bookings by Day of Week (Bar Chart)**
   - X-axis: Days of the week
   - Y-axis: Number of bookings
   - Color-coded by booking status
   - Stacked bar chart for better visualization

3. **Booking Status Distribution (Pie Chart)**
   - Segments: Confirmed, Pending, Cancelled, Completed, No-show
   - Interactive legend with toggle capability
   - Percentage labels on segments

4. **Peak Hours Heatmap**
   - X-axis: Days of the week
   - Y-axis: Hours of the day
   - Color intensity based on booking frequency
   - Hover tooltips with exact counts

### 2.3 State Management

#### 2.3.1 Dashboard State Structure

```typescript
interface DashboardState {
  // Date range filters
  dateRange: {
    start: string; // ISO date string
    end: string;   // ISO date string
  };
  
  // Loading states
  loading: {
    stats: boolean;
    bookings: boolean;
    calendar: boolean;
    charts: boolean;
  };
  
  // Data
  stats: DashboardStats;
  bookings: BookingListItem[];
  calendarData: Record<string, CalendarDay>;
  chartData: {
    bookingsOverTime: { date: string; count: number }[];
    bookingsByDayOfWeek: { day: string; count: number }[];
    bookingStatusDistribution: { status: string; count: number }[];
    peakHours: { day: string; hour: number; count: number }[][];
  };
  
  // UI state
  selectedBooking: number | null;
  selectedDate: Date | null;
  filters: {
    bookingStatus: string[];
    clientName: string;
    sortBy: string;
    sortOrder: 'asc' | 'desc';
  };
  
  // Errors
  errors: {
    stats: string | null;
    bookings: string | null;
    calendar: string | null;
    charts: string | null;
  };
}
```

#### 2.3.2 Data Fetching Strategy

```typescript
// Service layer for data fetching
class DashboardService {
  // Fetch dashboard statistics
  async getStats(startDate: string, endDate: string): Promise<DashboardStats> {
    // Implementation with caching and error handling
  }
  
  // Fetch bookings with pagination
  async getBookings(
    startDate: string, 
    endDate: string, 
    page: number, 
    limit: number,
    filters: BookingFilters
  ): Promise<PaginatedResponse<BookingListItem>> {
    // Implementation with sorting and filtering
  }
  
  // Fetch calendar availability data
  async getCalendarAvailability(
    year: number, 
    month: number
  ): Promise<Record<string, CalendarDay>> {
    // Implementation with bulk data fetching
  }
  
  // Fetch chart data
  async getChartData(
    startDate: string, 
    endDate: string
  ): Promise<ChartData> {
    // Implementation with data aggregation
  }
}
```

## 3. API Design

### 3.1 Enhanced Dashboard Endpoints

```python
# Dashboard statistics endpoint
@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(
    start_date: str = Query(...),
    end_date: str = Query(...),
    current_user: User = Depends(get_current_user)
) -> DashboardStatsResponse:
    """
    Get dashboard statistics for a date range
    """

# Paginated bookings endpoint
@app.get("/api/v1/dashboard/bookings")
async def get_dashboard_bookings(
    start_date: str = Query(...),
    end_date: str = Query(...),
    page: int = Query(1),
    limit: int = Query(50),
    status: Optional[str] = Query(None),
    sort_by: str = Query("date"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(get_current_user)
) -> PaginatedBookingsResponse:
    """
    Get paginated bookings for dashboard with filtering and sorting
    """

# Calendar availability endpoint
@app.get("/api/v1/dashboard/calendar-availability")
async def get_calendar_availability(
    year: int = Query(...),
    month: int = Query(...),
    current_user: User = Depends(get_current_user)
) -> CalendarAvailabilityResponse:
    """
    Get calendar availability data for a month
    """

# Chart data endpoint
@app.get("/api/v1/dashboard/chart-data")
async def get_chart_data(
    start_date: str = Query(...),
    end_date: str = Query(...),
    current_user: User = Depends(get_current_user)
) -> ChartDataResponse:
    """
    Get aggregated data for dashboard charts
    """
```

## 4. Performance Optimization

### 4.1 Virtual Scrolling for Booking List

Implementation of virtual scrolling to handle large datasets efficiently:

```typescript
import { FixedSizeList as List } from 'react-window';

const VirtualizedBookingList: React.FC<BookingListProps> = ({
  bookings,
  onBookingSelect,
  onStatusChange
}) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <BookingListItem
        booking={bookings[index]}
        onSelect={onBookingSelect}
        onStatusChange={onStatusChange}
      />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={bookings.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </List>
  );
};
```

### 4.2 Data Caching Strategy

```typescript
// Zustand store for dashboard data caching
interface DashboardStore {
  // Cached data with timestamps
  cachedData: {
    stats: { data: DashboardStats; timestamp: number };
    bookings: { data: BookingListItem[]; timestamp: number; page: number };
    calendar: { data: Record<string, CalendarDay>; timestamp: number; month: string };
    charts: { data: ChartData; timestamp: number };
  };
  
  // Cache duration (5 minutes for most data)
  cacheDuration: number;
  
  // Methods to check cache validity
  isCacheValid: (cacheKey: string) => boolean;
  
  // Methods to update cache
  updateCache: (cacheKey: string, data: any) => void;
}

// Implementation of caching with Zustand
const useDashboardStore = create<DashboardStore>((set, get) => ({
  cachedData: {
    stats: { data: null, timestamp: 0 },
    bookings: { data: [], timestamp: 0, page: 1 },
    calendar: { data: {}, timestamp: 0, month: '' },
    charts: { data: null, timestamp: 0 }
  },
  cacheDuration: 5 * 60 * 1000, // 5 minutes
  
  isCacheValid: (cacheKey) => {
    const { cachedData, cacheDuration } = get();
    const cacheEntry = cachedData[cacheKey as keyof typeof cachedData];
    if (!cacheEntry || !cacheEntry.timestamp) return false;
    
    return Date.now() - cacheEntry.timestamp < cacheDuration;
  },
  
  updateCache: (cacheKey, data) => {
    set((state) => ({
      cachedData: {
        ...state.cachedData,
        [cacheKey]: { data, timestamp: Date.now() }
      }
    }));
  }
}));
```

### 4.3 Lazy Loading for Charts

```typescript
// Lazy load chart components only when they come into view
const ChartContainer: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const chartRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    
    if (chartRef.current) {
      observer.observe(chartRef.current);
    }
    
    return () => {
      observer.disconnect();
    };
  }, []);
  
  return (
    <div ref={chartRef} className="chart-container">
      {isVisible ? <InteractiveChart /> : <LoadingPlaceholder />}
    </div>
  );
};
```

### 4.4 Data Pagination and Filtering

To improve performance with large datasets, implement server-side pagination and filtering:

```typescript
// Service layer for paginated data fetching
const DashboardService = {
  // Fetch paginated bookings
  async getBookings(
    filters: BookingFilters,
    pagination: { page: number; limit: number },
    sort: { field: string; order: 'asc' | 'desc' }
  ): Promise<{ bookings: BookingListItem[]; totalCount: number }> {
    const params = new URLSearchParams({
      ...filters,
      page: pagination.page.toString(),
      limit: pagination.limit.toString(),
      sortField: sort.field,
      sortOrder: sort.order
    });
    
    const response = await fetch(`/api/dashboard/bookings?${params}`);
    return response.json();
  },
  
  // Debounced search to reduce API calls
  debounceSearch: debounce(async (query: string, callback: Function) => {
    const response = await fetch(`/api/dashboard/bookings/search?q=${encodeURIComponent(query)}`);
    const results = await response.json();
    callback(results);
  }, 300)
};

// Debounce utility function
function debounce(func: Function, wait: number) {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
  };
  clearTimeout(timeout);
  timeout = setTimeout(later, wait);
  };
}
```

### 4.5 Component Memoization

Use React.memo and useMemo to prevent unnecessary re-renders:

```typescript
// Memoized booking list item
const BookingListItem = React.memo(({ 
  booking, 
  onSelect, 
  onStatusChange 
}: {
  booking: BookingListItem;
  onSelect: (id: number) => void;
  onStatusChange: (id: number, status: string) => void;
}) => {
  return (
    <div className="booking-list-item">
      <div>{booking.reference}</div>
      <div>{booking.clientName}</div>
      <div>{booking.date}</div>
      <div>{booking.status}</div>
      <div>{booking.totalPrice}</div>
      <button onClick={() => onSelect(booking.id)}>View</button>
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function to prevent re-renders
  return prevProps.booking.id === nextProps.booking.id &&
         prevProps.booking.status === nextProps.booking.status;
});

// Memoized chart component
const MemoizedChart = React.memo(({ data }: { data: ChartData }) => {
  // Chart implementation
  return <ChartComponent data={data} />;
}, (prevProps, nextProps) => {
  // Deep comparison of chart data
  return JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data);
});
```

## 5. Accessibility and Responsive Design

### 5.1 Keyboard Navigation

- Tab navigation through all interactive elements
- Arrow key navigation for calendar dates
- Enter key activation for buttons and links
- Proper focus indicators for all interactive elements

### 5.2 Screen Reader Support

- ARIA labels for all interactive elements
- Proper heading hierarchy (h1, h2, h3, etc.)
- Descriptive alt text for icons and images
- Live regions for dynamic content updates

### 5.3 Responsive Design

- Mobile-first approach with progressive enhancement
- Flexible grid layout using CSS Grid and Flexbox
- Media queries for different screen sizes
- Touch-friendly interface elements

## 6. Error Handling and User Feedback

### 6.1 Error Boundaries

Implement error boundaries to gracefully handle component errors:

```typescript
// Error boundary component
class DashboardErrorBoundary extends React.Component<{}, { hasError: boolean; error: Error | null }> {
  constructor(props: {}) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to monitoring service
    console.error('Dashboard error:', error, errorInfo);
    // Send to error tracking service
    // errorTrackingService.report(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-container">
          <h2>Что-то пошло не так</h2>
          <p>Произошла ошибка при загрузке дашборда. Пожалуйста, попробуйте обновить страницу.</p>
          <button onClick={() => window.location.reload()}>Обновить страницу</button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 6.2 User Feedback Mechanisms

Provide clear feedback for user actions:

```typescript
// Toast notification system
const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
    const id = Date.now();
    const newToast = { id, message, type };
    
    setToasts(prev => [...prev, newToast]);
    
    // Auto-remove toast after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 5000);
  };

  const removeToast = (id: number) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  return { toasts, addToast, removeToast };
};

// Loading states with skeleton screens
const LoadingSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
);

// Progress indicators for long-running operations
const ProgressBar: React.FC<{ progress: number }> = ({ progress }) => (
  <div className="w-full bg-gray-200 rounded-full h-2.5">
    <div 
      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
      style={{ width: `${progress}%` }}
    ></div>
  </div>
);
```

### 6.3 Retry Mechanisms

Implement retry mechanisms for failed operations:

```typescript
// Retry utility with exponential backoff
const useRetry = (maxRetries: number = 3) => {
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);

  const retry = async <T,>(operation: () => Promise<T>): Promise<T | null> => {
    setIsRetrying(true);
    
    try {
      const result = await operation();
      setRetryCount(0);
      setIsRetrying(false);
      return result;
    } catch (error) {
      if (retryCount < maxRetries) {
        // Exponential backoff: 1s, 2s, 4s, etc.
        const delay = Math.pow(2, retryCount) * 1000;
        
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          retry(operation);
        }, delay);
      } else {
        setIsRetrying(false);
        throw error;
      }
    }
    
    return null;
  };

  return { retry, retryCount, isRetrying };
};
```

## 6. Real-time Updates

### 6.1 WebSocket Integration

```typescript
// WebSocket service for real-time updates
class DashboardWebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private listeners: Map<string, Function[]> = new Map();
  
  connect(userId: number): void {
    // Establish WebSocket connection
    this.socket = new WebSocket(`ws://localhost:8000/ws/dashboard/${userId}`);
    
    this.socket.onopen = () => {
      console.log('WebSocket connection established');
      this.reconnectAttempts = 0; // Reset reconnect attempts on successful connection
    };
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket connection closed');
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect(userId);
        }, 1000 * this.reconnectAttempts); // Exponential backoff
      }
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  // Add event listener
  addListener(eventType: string, callback: Function): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)!.push(callback);
  }
  
  // Remove event listener
  removeListener(eventType: string, callback: Function): void {
    const callbacks = this.listeners.get(eventType);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }
  
  private handleMessage(data: WebSocketMessage): void {
    // Notify all listeners of the event
    const callbacks = this.listeners.get(data.type);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
    
    // Update dashboard state based on message type
    switch (data.type) {
      case 'BOOKING_CREATED':
        // Add new booking to list
        this.notifyListeners('bookingCreated', data.payload);
        break;
      case 'BOOKING_UPDATED':
        // Update existing booking
        this.notifyListeners('bookingUpdated', data.payload);
        break;
      case 'BOOKING_DELETED':
        // Remove booking from list
        this.notifyListeners('bookingDeleted', data.payload);
        break;
      case 'CALENDAR_UPDATED':
        // Update calendar availability
        this.notifyListeners('calendarUpdated', data.payload);
        break;
    }
  }
  
  private notifyListeners(eventType: string, payload: any): void {
    const callbacks = this.listeners.get(eventType);
    if (callbacks) {
      callbacks.forEach(callback => callback(payload));
    }
  }
  
  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

// React hook for using WebSocket in components
const useDashboardWebSocket = (userId: number) => {
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [lastMessage, setLastMessage] = useState<any>(null);
  
  const webSocketService = useMemo(() => new DashboardWebSocketService(), []);
  
  useEffect(() => {
    if (userId) {
      webSocketService.connect(userId);
      
      // Listen for connection status changes
      webSocketService.addListener('connectionStatus', (status) => {
        setConnectionStatus(status);
      });
      
      // Listen for messages
      webSocketService.addListener('message', (message) => {
        setLastMessage(message);
      });
    }
    
    return () => {
      webSocketService.disconnect();
    };
  }, [userId, webSocketService]);
  
  return { connectionStatus, lastMessage, webSocketService };
};
```

### 6.2 Real-time Dashboard Updates

The dashboard components will be updated in real-time using the WebSocket service:

```typescript
// Dashboard component with real-time updates
const Dashboard: React.FC = () => {
  const [bookings, setBookings] = useState<BookingListItem[]>([]);
  const [calendarData, setCalendarData] = useState<Record<string, CalendarDay>>({});
  const [stats, setStats] = useState<DashboardStats>(initialStats);
  
  // Get user ID from auth context
  const { user } = useAuth();
  
  // Initialize WebSocket connection
  const { webSocketService } = useDashboardWebSocket(user?.id);
  
  // Set up WebSocket listeners
  useEffect(() => {
    // Listen for new bookings
    webSocketService.addListener('bookingCreated', (newBooking: BookingListItem) => {
      setBookings(prev => [newBooking, ...prev]);
      // Update stats
      setStats(prev => ({
        ...prev,
        totalBookings: prev.totalBookings + 1
      }));
    });
    
    // Listen for booking updates
    webSocketService.addListener('bookingUpdated', (updatedBooking: BookingListItem) => {
      setBookings(prev => 
        prev.map(booking => 
          booking.id === updatedBooking.id ? updatedBooking : booking
        )
      );
    });
    
    // Listen for booking deletions
    webSocketService.addListener('bookingDeleted', (deletedBookingId: number) => {
      setBookings(prev => prev.filter(booking => booking.id !== deletedBookingId));
      // Update stats
      setStats(prev => ({
        ...prev,
        totalBookings: prev.totalBookings - 1
      }));
    });
    
    // Listen for calendar updates
    webSocketService.addListener('calendarUpdated', (updatedCalendarData: Record<string, CalendarDay>) => {
      setCalendarData(prev => ({ ...prev, ...updatedCalendarData }));
    });
    
    // Clean up listeners
    return () => {
      webSocketService.removeListener('bookingCreated', () => {});
      webSocketService.removeListener('bookingUpdated', () => {});
      webSocketService.removeListener('bookingDeleted', () => {});
      webSocketService.removeListener('calendarUpdated', () => {});
    };
  }, [webSocketService]);
  
  // Rest of dashboard implementation...
};
```

## 7. Testing Strategy

### 7.1 Unit Tests

```typescript
// Test cases for dashboard components
describe('Dashboard Components', () => {
  test('BookingList renders correctly with data', () => {
    // Test with mock booking data
  });
  
  test('BookingList handles empty state', () => {
    // Test with no bookings
  });
  
  test('Calendar component displays correct availability', () => {
    // Test with mock availability data
  });
  
  test('Chart components render with correct data', () => {
    // Test each chart type with mock data
  });
});
```

### 7.2 Integration Tests

```typescript
// Test dashboard data fetching and state management
describe('Dashboard Data Flow', () => {
  test('Dashboard fetches and displays stats correctly', async () => {
    // Mock API responses and verify state updates
  });
  
  test('Dashboard handles API errors gracefully', async () => {
    // Mock API errors and verify error handling
  });
  
  test('Dashboard updates in real-time with WebSocket', () => {
    // Mock WebSocket messages and verify UI updates
  });
});
```

### 7.3 End-to-End Tests

```typescript
// Test complete dashboard user flows
describe('Dashboard User Flows', () => {
  test('User can filter bookings by date range', async () => {
    // Navigate to dashboard
    // Set date range
    // Verify bookings are filtered correctly
  });
  
  test('User can sort bookings by different criteria', async () => {
    // Navigate to dashboard
    // Select sort option
    // Verify bookings are sorted correctly
  });
  
  test('User can interact with calendar to view bookings', async () => {
    // Navigate to dashboard
    // Click on calendar date
    // Verify booking details are displayed
  });
});
```

## 8. Security Considerations

### 8.1 Authentication and Authorization

- Role-based access control for dashboard features
- Proper authentication checks for all API endpoints
- Secure WebSocket connections with token authentication
- Protection against CSRF attacks

### 8.2 Data Protection

- Encryption of sensitive data in transit and at rest
- Proper data sanitization to prevent XSS attacks
- Rate limiting for API endpoints to prevent abuse
- Secure storage of authentication tokens

## 9. Deployment Considerations

### 9.1 Performance Monitoring

- Integration with performance monitoring tools
- Error tracking and reporting
- User experience metrics collection
- Automated alerts for performance degradation

### 9.2 Scalability

- Horizontal scaling of backend services
- Database optimization for large datasets
- Caching strategies for improved performance
- Load balancing for high availability

## 10. Future Enhancements

### 10.1 Advanced Analytics

- Predictive analytics for booking trends
- Customer lifetime value calculations
- Revenue forecasting models
- Custom report generation

### 10.2 Mobile Optimization

- Dedicated mobile app for dashboard access
- Push notifications for important updates
- Offline functionality for basic features
- Mobile-specific UI optimizations

### 10.3 AI-Powered Features

- Intelligent booking recommendations
- Automated scheduling optimization
- Customer sentiment analysis
- Dynamic pricing suggestions

## 11. Conclusion

The enhanced dashboard interface addresses all the key issues identified in the current implementation:

1. **Scrollable Booking List**: Implemented virtual scrolling and pagination to handle large datasets efficiently
2. **Interactive Elements**: Added expandable rows, hover effects, and action buttons for better user engagement
3. **Schedule Visualization**: Created an interactive calendar component with color-coded availability indicators
4. **Data Visualization**: Integrated Chart.js for interactive charts with real-time updates
5. **Responsive Design**: Implemented a flexible grid layout that adapts to different screen sizes
6. **Real-time Updates**: Added WebSocket integration for live data updates
7. **Performance Optimization**: Used caching, memoization, and lazy loading to improve performance
8. **Error Handling**: Implemented comprehensive error boundaries and user feedback mechanisms

These enhancements will significantly improve the user experience for staff members managing the photo studio, providing them with a more efficient and informative interface for monitoring and managing bookings.




























































































































