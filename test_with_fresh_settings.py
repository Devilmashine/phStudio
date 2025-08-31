import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Clear the settings cache
import functools
from backend.app.core.config import get_settings

# Clear the cache
get_settings.cache_clear()

async def test_with_fresh_settings():
    """Test with fresh settings"""
    print("Testing with fresh settings...")
    
    # Get fresh settings
    settings = get_settings()
    
    print(f"TELEGRAM_BOT_TOKEN: {settings.TELEGRAM_BOT_TOKEN}")
    print(f"TELEGRAM_CHAT_ID: {settings.TELEGRAM_CHAT_ID}")
    
    try:
        # Import the TelegramBotService directly
        from backend.app.services.telegram_bot import TelegramBotService
        
        # Create the service exactly as it's done in booking notification service
        bot_service = TelegramBotService()
        
        print(f"Bot token from service: {bot_service.bot_token}")
        print(f"Chat ID from service: {bot_service.chat_id}")
        
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
    asyncio.run(test_with_fresh_settings())