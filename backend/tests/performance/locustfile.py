"""
Load Testing Framework using Locust
Performance testing for the Photo Studio API
"""

from locust import HttpUser, task, between, events
from datetime import datetime, timedelta
import random
import string
import json

class BookingUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    def on_start(self):
        """Initialize user session"""
        # Login as test user
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        # Note: In real testing, you would authenticate here
        # For now, we'll simulate authenticated requests
        
    @task(3)
    def view_bookings_list(self):
        """View list of bookings (most common operation)"""
        self.client.get("/api/bookings/", name="View Bookings List")
    
    @task(2)
    def view_booking_details(self):
        """View specific booking details"""
        booking_id = random.randint(1, 100)
        self.client.get(f"/api/bookings/{booking_id}", name="View Booking Details")
    
    @task(1)
    def create_booking(self):
        """Create a new booking"""
        # Generate random booking data
        client_name = f"Client {''.join(random.choices(string.ascii_letters, k=8))}"
        client_phone = f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"
        
        # Generate future date
        future_date = datetime.now() + timedelta(days=random.randint(1, 30))
        start_time = future_date.replace(hour=random.randint(9, 18), minute=0, second=0)
        end_time = start_time + timedelta(hours=random.randint(1, 3))
        
        booking_data = {
            "date": future_date.date().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_price": random.randint(1000, 5000),
            "client_name": client_name,
            "client_phone": client_phone
        }
        
        self.client.post("/api/bookings/", 
                        json=booking_data,
                        headers={"Content-Type": "application/json"},
                        name="Create Booking")
    
    @task(1)
    def search_bookings(self):
        """Search for bookings by client name"""
        client_names = ["Ivanov", "Petrov", "Sidorov", "Smirnov", "Vasiliev"]
        search_name = random.choice(client_names)
        self.client.get(f"/api/bookings/?client_name={search_name}", name="Search Bookings")
    
    @task(1)
    def view_calendar(self):
        """View calendar events"""
        self.client.get("/api/calendar/", name="View Calendar")
    
    @task(1)
    def view_gallery(self):
        """View gallery images"""
        self.client.get("/api/gallery/", name="View Gallery")
    
    @task(1)
    def view_news(self):
        """View news articles"""
        self.client.get("/api/news/", name="View News")

class AdminUser(HttpUser):
    wait_time = between(2, 10)  # Wait 2-10 seconds between tasks
    
    def on_start(self):
        """Initialize admin session"""
        # Login as admin user
        pass
    
    @task(2)
    def view_admin_dashboard(self):
        """View admin dashboard"""
        self.client.get("/api/admin/dashboard", name="View Admin Dashboard")
    
    @task(1)
    def view_all_bookings(self):
        """View all bookings with filters"""
        self.client.get("/api/bookings/?limit=50", name="View All Bookings")
    
    @task(1)
    def manage_users(self):
        """Manage users"""
        self.client.get("/api/users/", name="Manage Users")
    
    @task(1)
    def view_statistics(self):
        """View system statistics"""
        self.client.get("/api/admin/stats", name="View Statistics")

# Performance monitoring events
@events.request.add_listener
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    """Track successful requests"""
    if response_time > 1000:  # Log slow requests (>1 second)
        print(f"SLOW REQUEST: {name} took {response_time}ms")

@events.request.add_listener
def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
    """Track failed requests"""
    print(f"FAILED REQUEST: {name} failed with {exception}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Test start event"""
    print("Performance test started")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Test stop event"""
    print("Performance test completed")