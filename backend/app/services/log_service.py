import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "actions.log")

def log_action(user: str, action: str, details: str = ""):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {user} | {action} | {details}\n")

def export_logs() -> str:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read() 