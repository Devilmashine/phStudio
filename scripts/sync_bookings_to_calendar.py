#!/usr/bin/env python3
"""
Script to sync existing bookings to calendar events
"""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import get_session_local
from app.models.booking import Booking
from app.models.calendar_event import CalendarEvent
from app.schemas.calendar_event import CalendarEventCreate
from app.services.calendar_event import CalendarEventService
from datetime import datetime

def sync_bookings_to_calendar():
    """Sync all existing bookings to calendar events"""
    # Correctly get the session maker
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        # Get all bookings
        bookings = db.query(Booking).all()
        print(f"Found {len(bookings)} bookings to sync")
        
        # Get calendar event service
        calendar_service = CalendarEventService(db)
        
        # Count how many events we create
        created_count = 0
        skipped_count = 0
        linked_count = 0
        
        for booking in bookings:
            # Check if a calendar event already exists for this booking
            existing_event = db.query(CalendarEvent).filter(
                CalendarEvent.title.like(f"%{booking.client_name}%"),
                CalendarEvent.start_time == booking.start_time,
                CalendarEvent.end_time == booking.end_time
            ).first()
            
            if existing_event:
                # If event exists but booking is not linked, link them
                if booking.calendar_event_id is None:
                    booking.calendar_event_id = existing_event.id
                    db.commit()
                    linked_count += 1
                    print(f"Linked booking {booking.id} to existing event {existing_event.id}")
                else:
                    print(f"Skipping booking {booking.id} - event already exists and linked")
                skipped_count += 1
                continue
            
            # Create calendar event for this booking
            try:
                event_data = CalendarEventCreate(
                    title=f"Бронирование: {booking.client_name}",
                    description=f"Клиент: {booking.client_name}\nТелефон: {booking.client_phone}\nEmail: {booking.client_email or 'Не указан'}\nКоличество человек: {booking.people_count}",
                    start_time=booking.start_time,
                    end_time=booking.end_time,
                    people_count=booking.people_count,
                    status="pending"  # Default status
                )
                
                event = calendar_service.create_event(event_data)
                
                # Link the booking to the calendar event
                booking.calendar_event_id = event.id
                db.commit()
                
                created_count += 1
                print(f"Created calendar event {event.id} for booking {booking.id}")
                
            except Exception as e:
                print(f"Error creating event for booking {booking.id}: {e}")
                continue
        
        print(f"Sync complete: {created_count} events created, {skipped_count} skipped, {linked_count} linked")
        return True
        
    except Exception as e:
        print(f"Error during sync: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Syncing bookings to calendar events...")
    success = sync_bookings_to_calendar()
    if success:
        print("✅ Sync completed successfully")
        sys.exit(0)
    else:
        print("❌ Sync failed")
        sys.exit(1)