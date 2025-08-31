import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.config import get_settings

async def debug_telegram():
    """Debug Telegram configuration"""
    print("Debugging Telegram configuration...")
    
    # Load settings
    settings = get_settings()
    
    print(f"ENV: {settings.ENV}")
    print(f"TELEGRAM_BOT_TOKEN: {settings.TELEGRAM_BOT_TOKEN}")
    print(f"TELEGRAM_CHAT_ID: {settings.TELEGRAM_CHAT_ID}")
    
    # Validate configuration
    is_valid = settings.validate_telegram_config()
    print(f"Configuration valid: {is_valid}")
    
    if not is_valid:
        print("Configuration validation failed!")
        return
    
    # Show token and chat ID details
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    print(f"Token length: {len(token)}")
    print(f"Token format valid: {':' in token}")
    print(f"Chat ID format valid: {chat_id.startswith('-') or chat_id.isdigit()}")
    
    # Try to import and test the Telegram service
    try:
        from backend.app.services.telegram_bot import TelegramBotService
        bot_service = TelegramBotService()
        
        print(f"Service bot token: {bot_service.bot_token}")
        print(f"Service chat ID: {bot_service.chat_id}")
        print(f"Service API URL: {bot_service.api_url}")
        
        # Test a simple GET request to see if the token works
        import aiohttp
        import ssl
        
        # Create SSL context that handles certificate verification
        ssl_context = ssl.create_default_context()
        # For development environments with SSL certificate issues
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        # Test getMe endpoint
        test_url = f"https://api.telegram.org/bot{token}/getMe"
        print(f"Testing getMe endpoint: {test_url}")
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(test_url) as resp:
                print(f"getMe response status: {resp.status}")
                response_text = await resp.text()
                print(f"getMe response: {response_text}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_telegram())