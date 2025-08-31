#!/usr/bin/env python3
"""
Script to populate the database with realistic test data for all CRM and administrative sections.
This script creates test data for users, employees, clients, bookings, news, gallery images, and calendar events.
"""

import os
import sys
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
import random

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.database import get_engine, get_session_local
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.models.client import Client
from app.models.booking import Booking, BookingStatus
from app.models.news import News
from app.models.gallery import GalleryImage
from app.models.calendar_event import CalendarEvent
from app.models.base import Base

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_session():
    """Get database session"""
    engine = get_engine()
    SessionLocal = get_session_local()
    return SessionLocal()

def create_test_users(db: Session):
    """Create test users with different roles"""
    print("Creating test users...")
    
    # Common password for all test users
    test_password = "TestPass123!"
    hashed_password = pwd_context.hash(test_password)
    
    # Create users with different roles
    users_data = [
        {
            "username": "testuser",
            "email": "user@test.com",
            "full_name": "Test User",
            "role": UserRole.user,
            "hashed_password": hashed_password,
            "ical_token": token_urlsafe(32),
            "is_active": "true"
        },
        {
            "username": "testadmin",
            "email": "admin@test.com",
            "full_name": "Test Admin",
            "role": UserRole.admin,
            "hashed_password": hashed_password,
            "ical_token": token_urlsafe(32),
            "is_active": "true"
        },
        {
            "username": "testmanager",
            "email": "manager@test.com",
            "full_name": "Test Manager",
            "role": UserRole.manager,
            "hashed_password": hashed_password,
            "ical_token": token_urlsafe(32),
            "is_active": "true"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            created_users.append(existing_user)
            continue
            
        user = User(**user_data)
        db.add(user)
        created_users.append(user)
    
    db.commit()
    
    # Refresh to get IDs
    for user in created_users:
        db.refresh(user)
    
    print(f"Created/verified {len(created_users)} test users:")
    for user in created_users:
        print(f"  - {user.username} ({user.role.value}) - Password: {test_password}")
    
    return created_users

def create_test_employees(db: Session):
    """Create test employees"""
    print("Creating test employees...")
    
    # Create employees with different positions
    employees_data = [
        {
            "full_name": "Alex Johnson",
            "position": "Owner",
            "email": "alex.johnson@company.com",
            "phone": "+1234567890",
            "is_active": True,
            "hire_date": datetime.now(timezone.utc).date() - timedelta(days=365)
        },
        {
            "full_name": "Maria Garcia",
            "position": "System Administrator",
            "email": "maria.garcia@company.com",
            "phone": "+1234567891",
            "is_active": True,
            "hire_date": datetime.now(timezone.utc).date() - timedelta(days=180)
        },
        {
            "full_name": "James Wilson",
            "position": "Operations Manager",
            "email": "james.wilson@company.com",
            "phone": "+1234567892",
            "is_active": True,
            "hire_date": datetime.now(timezone.utc).date() - timedelta(days=90)
        },
        {
            "full_name": "Sarah Davis",
            "position": "Senior Photographer",
            "email": "sarah.davis@company.com",
            "phone": "+1234567893",
            "is_active": True,
            "hire_date": datetime.now(timezone.utc).date() - timedelta(days=60)
        },
        {
            "full_name": "Robert Miller",
            "position": "Photographer",
            "email": "robert.miller@company.com",
            "phone": "+1234567894",
            "is_active": True,
            "hire_date": datetime.now(timezone.utc).date() - timedelta(days=45)
        },
        {
            "full_name": "Emily Brown",
            "position": "Assistant Photographer",
            "email": "emily.brown@company.com",
            "phone": "+1234567895",
            "is_active": True,
            "hire_date": datetime.now(timezone.utc).date() - timedelta(days=30)
        }
    ]
    
    created_employees = []
    for emp_data in employees_data:
        # Check if employee already exists
        existing_employee = db.query(Employee).filter(Employee.email == emp_data["email"]).first()
        if existing_employee:
            print(f"Employee {emp_data['full_name']} already exists, skipping...")
            created_employees.append(existing_employee)
            continue
            
        employee = Employee(**emp_data)
        db.add(employee)
        created_employees.append(employee)
    
    db.commit()
    
    # Refresh to get IDs
    for employee in created_employees:
        db.refresh(employee)
    
    print(f"Created/verified {len(created_employees)} test employees:")
    for employee in created_employees:
        print(f"  - {employee.full_name} ({employee.position}) - Email: {employee.email}")
    
    return created_employees

def create_test_clients(db: Session):
    """Create test clients"""
    print("Creating test clients...")
    
    # Client names and phone numbers
    client_data = [
        ("John Smith", "+1345678901"),
        ("Emma Thompson", "+1345678902"),
        ("Michael Brown", "+1345678903"),
        ("Sophia Davis", "+1345678904"),
        ("William Johnson", "+1345678905"),
        ("Olivia Wilson", "+1345678906"),
        ("James Miller", "+1345678907"),
        ("Ava Taylor", "+1345678908"),
        ("Benjamin Anderson", "+1345678909"),
        ("Mia Thomas", "+1345678910"),
        ("Elijah Jackson", "+1345678911"),
        ("Charlotte White", "+1345678912"),
        ("Lucas Harris", "+1345678913"),
        ("Amelia Martin", "+1345678914"),
        ("Mason Thompson", "+1345678915"),
    ]
    
    created_clients = []
    for name, phone in client_data:
        # Check if client already exists
        existing_client = db.query(Client).filter(Client.phone == phone).first()
        if existing_client:
            print(f"Client {name} already exists, skipping...")
            created_clients.append(existing_client)
            continue
            
        client = Client(
            name=name,
            phone=phone,
            is_active=True
        )
        db.add(client)
        created_clients.append(client)
    
    db.commit()
    
    # Refresh to get IDs
    for client in created_clients:
        db.refresh(client)
    
    print(f"Created/verified {len(created_clients)} test clients:")
    for client in created_clients:
        print(f"  - {client.name} - Phone: {client.phone}")
    
    return created_clients

def create_test_bookings(db: Session, clients, employees):
    """Create test bookings"""
    print("Creating test bookings...")
    
    # Service types
    service_types = [
        "Portrait Session",
        "Family Photo Shoot",
        "Wedding Photography",
        "Corporate Event",
        "Product Photography",
        "Fashion Shoot"
    ]
    
    # Create bookings for the next 30 days
    created_bookings = []
    now = datetime.now(timezone.utc)
    
    for i in range(30):
        # Random date in the next 30 days
        booking_date = now + timedelta(days=random.randint(1, 30))
        
        # Random start time between 9 AM and 5 PM
        start_hour = random.randint(9, 17)
        start_time = booking_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=random.randint(1, 3))
        
        # Random client
        client = random.choice(clients)
        
        # Random service type
        service_type = random.choice(service_types)
        
        # Random employee (photographer)
        employee = random.choice(employees)
        
        # Random status
        statuses = list(BookingStatus)
        status = random.choice(statuses)
        
        # Random price
        total_price = round(random.uniform(100.0, 1000.0), 2)
        
        # Check if booking already exists
        existing_booking = db.query(Booking).filter(
            Booking.start_time == start_time,
            Booking.client_name == client.name
        ).first()
        
        if existing_booking:
            print(f"Booking for {client.name} at {start_time} already exists, skipping...")
            created_bookings.append(existing_booking)
            continue
            
        booking = Booking(
            date=booking_date.date(),
            start_time=start_time,
            end_time=end_time,
            status=status,
            total_price=total_price,
            client_name=client.name,
            client_phone=client.phone,
            phone_normalized=client.phone,
            notes=f"Booking for {service_type}",
            people_count=random.randint(1, 10),
            service_type=service_type,
            source="website",
            payment_status="pending" if status == BookingStatus.PENDING else "confirmed",
            assigned_to=employee.id
        )
        db.add(booking)
        created_bookings.append(booking)
    
    db.commit()
    
    # Refresh to get IDs
    for booking in created_bookings:
        db.refresh(booking)
    
    print(f"Created/verified {len(created_bookings)} test bookings")
    
    # Show some sample bookings
    for booking in created_bookings[:5]:
        print(f"  - {booking.client_name} - {booking.service_type} - {booking.start_time} - {booking.status.value}")
    
    return created_bookings

def create_test_news(db: Session, users):
    """Create test news articles"""
    print("Creating test news articles...")
    
    # News titles and content
    news_data = [
        {
            "title": "New Studio Location",
            "content": "We're excited to announce our new studio location in the heart of downtown. With more space and better lighting, we can now accommodate larger photo shoots and events.",
            "summary": "Announcing our new downtown studio location",
            "tags": "studio,location,announcement",
            "featured": True
        },
        {
            "title": "Summer Special Offers",
            "content": "Take advantage of our summer special offers on family portraits and wedding photography. Book before the end of August and save up to 20% on your session.",
            "summary": "Special summer discounts on photography services",
            "tags": "summer,special,discount",
            "featured": True
        },
        {
            "title": "New Equipment Arrival",
            "content": "We've upgraded our photography equipment with the latest Canon cameras and professional lighting systems. This allows us to deliver even higher quality images to our clients.",
            "summary": "Upgraded photography equipment for better quality",
            "tags": "equipment,upgrade,quality",
            "featured": False
        },
        {
            "title": "Workshop Registration Open",
            "content": "Registration is now open for our photography workshops. Learn from our professional photographers and improve your skills. Limited spots available!",
            "summary": "Photography workshops registration now open",
            "tags": "workshop,education,registration",
            "featured": False
        },
        {
            "title": "Holiday Hours Announcement",
            "content": "Please note our adjusted holiday hours for the upcoming season. We will be closed on major holidays but open for extended hours on weekends.",
            "summary": "Adjusted holiday hours for upcoming season",
            "tags": "holiday,hours,announcement",
            "featured": False
        }
    ]
    
    created_news = []
    for i, news_item in enumerate(news_data):
        # Check if news article already exists
        existing_news = db.query(News).filter(News.title == news_item["title"]).first()
        if existing_news:
            print(f"News article '{news_item['title']}' already exists, skipping...")
            created_news.append(existing_news)
            continue
            
        # Use the first admin user as author, or first user if no admin
        author = next((user for user in users if user.role == UserRole.admin), users[0])
        
        news = News(
            title=news_item["title"],
            content=news_item["content"],
            summary=news_item["summary"],
            tags=news_item["tags"],
            featured=news_item["featured"],
            author_id=author.id,
            published=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=len(news_data)-i),
            updated_at=datetime.now(timezone.utc) - timedelta(days=len(news_data)-i)
        )
        db.add(news)
        created_news.append(news)
    
    db.commit()
    
    # Refresh to get IDs
    for news in created_news:
        db.refresh(news)
    
    print(f"Created/verified {len(created_news)} test news articles:")
    for news in created_news:
        print(f"  - {news.title} - Featured: {news.featured}")
    
    return created_news

def create_test_gallery_images(db: Session):
    """Create test gallery images"""
    print("Creating test gallery images...")
    
    # Image data
    image_data = [
        {
            "title": "Sunset Portrait",
            "description": "Beautiful sunset portrait session with natural lighting",
            "image_url": "https://example.com/images/sunset-portrait.jpg",
            "thumbnail_url": "https://example.com/images/sunset-portrait-thumb.jpg",
            "category": "portraits"
        },
        {
            "title": "Family Photo Shoot",
            "description": "Happy family photo shoot in our studio",
            "image_url": "https://example.com/images/family-shoot.jpg",
            "thumbnail_url": "https://example.com/images/family-shoot-thumb.jpg",
            "category": "family"
        },
        {
            "title": "Wedding Ceremony",
            "description": "Candid shot from a beautiful outdoor wedding ceremony",
            "image_url": "https://example.com/images/wedding-ceremony.jpg",
            "thumbnail_url": "https://example.com/images/wedding-ceremony-thumb.jpg",
            "category": "weddings"
        },
        {
            "title": "Corporate Headshot",
            "description": "Professional corporate headshot with studio lighting",
            "image_url": "https://example.com/images/corporate-headshot.jpg",
            "thumbnail_url": "https://example.com/images/corporate-headshot-thumb.jpg",
            "category": "corporate"
        },
        {
            "title": "Nature Landscape",
            "description": "Stunning landscape photo from our outdoor session",
            "image_url": "https://example.com/images/nature-landscape.jpg",
            "thumbnail_url": "https://example.com/images/nature-landscape-thumb.jpg",
            "category": "landscapes"
        }
    ]
    
    created_images = []
    for img_data in image_data:
        # Check if image already exists
        existing_image = db.query(GalleryImage).filter(GalleryImage.title == img_data["title"]).first()
        if existing_image:
            print(f"Gallery image '{img_data['title']}' already exists, skipping...")
            created_images.append(existing_image)
            continue
            
        image = GalleryImage(
            title=img_data["title"],
            description=img_data["description"],
            image_url=img_data["image_url"],
            thumbnail_url=img_data["thumbnail_url"],
            category=img_data["category"],
            is_active=True,
            uploaded_at=datetime.now(timezone.utc)
        )
        db.add(image)
        created_images.append(image)
    
    db.commit()
    
    # Refresh to get IDs
    for image in created_images:
        db.refresh(image)
    
    print(f"Created/verified {len(created_images)} test gallery images:")
    for image in created_images:
        print(f"  - {image.title} - Category: {image.category}")
    
    return created_images

def main():
    """Main function to populate the database with test data"""
    print("=== Test Data Population Script ===")
    
    # Get database session
    db = get_db_session()
    
    try:
        # Create test users
        users = create_test_users(db)
        
        # Create test employees
        employees = create_test_employees(db)
        
        # Create test clients
        clients = create_test_clients(db)
        
        # Create test bookings
        bookings = create_test_bookings(db, clients, employees)
        
        # Create test news articles
        news = create_test_news(db, users)
        
        # Create test gallery images
        gallery_images = create_test_gallery_images(db)
        
        print("\n=== Summary ===")
        print(f"Users: {len(users)}")
        print(f"Employees: {len(employees)}")
        print(f"Clients: {len(clients)}")
        print(f"Bookings: {len(bookings)}")
        print(f"News Articles: {len(news)}")
        print(f"Gallery Images: {len(gallery_images)}")
        
        print("\nAll test data has been successfully created!")
        print("WARNING: This is test data. Do not use in production!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()