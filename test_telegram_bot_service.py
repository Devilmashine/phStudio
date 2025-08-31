import asyncio
import sys
import os
from datetime import date

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_telegram_bot_service():
    """Test TelegramBotService exactly as it's used in booking notification service"""
    print("Testing TelegramBotService...")
    
    try:
        # Import the TelegramBotService directly
        from backend.app.services.telegram_bot import TelegramBotService
        
        # Create the service exactly as it's done in booking notification service
        bot_service = TelegramBotService()
        
        print(f"Bot token: {bot_service.bot_token}")
        print(f"Chat ID: {bot_service.chat_id}")
        
        # Call send_booking_notification exactly as it's called in booking notification service
        success = await bot_service.send_booking_notification(
            message="Новое бронирование",
            booking_id="test_booking_001",
            service="Студийная фотосессия",
            date="01.09.2025",
            times=["10:00-11:00"],
            name="Test Client",
            phone="+79998887766",
            total_price=1000,
            people_count=1
        )
        
        if success:
            print("✅ Booking notification sent successfully!")
        else:
            print("❌ Failed to send booking notification")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram_bot_service())