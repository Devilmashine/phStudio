import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def debug_telegram_send():
    """Debug Telegram message sending"""
    print("Debugging Telegram message sending...")
    
    # Load settings
    from backend.app.core.config import get_settings
    settings = get_settings()
    
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    print(f"Using token: {token}")
    print(f"Using chat_id: {chat_id}")
    
    # Try to send a simple message using aiohttp
    try:
        import aiohttp
        import ssl
        import json
        
        # Create SSL context that handles certificate verification
        ssl_context = ssl.create_default_context()
        # For development environments with SSL certificate issues
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        # Test sendMessage endpoint
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
        print(f"Testing sendMessage endpoint: {send_url}")
        
        payload = {
            "chat_id": chat_id,
            "text": "Test message from phStudio debug script",
            "parse_mode": "HTML"
        }
        
        print(f"Sending payload: {json.dumps(payload, indent=2)}")
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(send_url, json=payload) as resp:
                print(f"sendMessage response status: {resp.status}")
                response_text = await resp.text()
                print(f"sendMessage response: {response_text}")
                
                if resp.status == 200:
                    print("✅ Message sent successfully!")
                else:
                    print("❌ Failed to send message")
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_telegram_send())