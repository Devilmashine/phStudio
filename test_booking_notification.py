import asyncio
import sys
import os
from datetime import date

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_booking_notification():
    """Test booking notification exactly as it's called in the app"""
    print("Testing booking notification...")
    
    try:
        # Import the booking notification service
        from backend.app.services.telegram.booking_notifications import booking_notification_service
        from backend.app.models.telegram import BookingData, Language
        
        # Create booking data similar to what's used in the app
        booking_data = BookingData(
            id="test_booking_001",
            service="Студийная фотосессия",
            date=date(2025, 9, 1),
            time_slots=["10:00-11:00"],
            client_name="Test Client",
            client_phone="+79998887766",
            people_count=1,
            total_price=1000.0,
            description="Test booking",
            status="pending"
        )
        
        print("Sending booking notification...")
        result = await booking_notification_service.send_booking_notification(
            booking_data=booking_data,
            language=Language.RU,
            queue=False  # Don't queue for this test
        )
        
        print(f"Notification result: {result}")
        if result.success:
            print("✅ Booking notification sent successfully!")
        else:
            print(f"❌ Failed to send booking notification: {result.error}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_booking_notification())