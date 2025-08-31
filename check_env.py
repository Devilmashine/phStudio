import os
from dotenv import load_dotenv

# Load environment variables
print("Loading .env file...")
load_dotenv()

print("Environment variables:")
print(f"TELEGRAM_BOT_TOKEN: {os.getenv('TELEGRAM_BOT_TOKEN')}")
print(f"TELEGRAM_CHAT_ID: {os.getenv('TELEGRAM_CHAT_ID')}")

# Try to load from specific path
print("\nTrying to load from specific path...")
load_dotenv('.env')

print("Environment variables after loading from .env:")
print(f"TELEGRAM_BOT_TOKEN: {os.getenv('TELEGRAM_BOT_TOKEN')}")
print(f"TELEGRAM_CHAT_ID: {os.getenv('TELEGRAM_CHAT_ID')}")

# Try to load from backend directory
print("\nTrying to load from backend directory...")
load_dotenv('backend/.env')

print("Environment variables after loading from backend/.env:")
print(f"TELEGRAM_BOT_TOKEN: {os.getenv('TELEGRAM_BOT_TOKEN')}")
print(f"TELEGRAM_CHAT_ID: {os.getenv('TELEGRAM_CHAT_ID')}")