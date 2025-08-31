import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.telegram_bot import TelegramBotService

async def test_telegram():
    """Test Telegram bot service"""
    print("Testing Telegram configuration...")
    
    try:
        # Initialize the service
        bot_service = TelegramBotService()
        
        print(f"Bot token: {bot_service.bot_token[:10]}...")  # Show only first 10 characters for security
        print(f"Chat ID: {bot_service.chat_id}")
        print(f"API URL: {bot_service.api_url}")
        
        # Test sending a simple message
        print("Sending test message...")
        success = await bot_service.send_booking_notification(
            message="Test notification",
            booking_id="test_001",
            service="Test Service",
            date="01.09.2025",
            times=["10:00-11:00"],
            name="Test User",
            phone="+79998887766",
            total_price=1000,
            people_count=1
        )
        
        if success:
            print("✅ Test message sent successfully!")
        else:
            print("❌ Failed to send test message")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram())