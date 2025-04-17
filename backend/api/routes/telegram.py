from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from backend.app.core.database import get_db

router = APIRouter(prefix="/telegram")
logger = logging.getLogger(__name__)

@router.post("/webhook", response_model=Dict[str, Any])
async def telegram_webhook(
    update: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Обработка webhook-запросов от Telegram"""
    logger.info(f"Получен апдейт от Telegram: {update}")
    message = update.get("message")
    if message:
        text = message.get("text", "")
        chat_id = message["chat"]["id"]
        # Пример: обработка команд
        if text.startswith("/start"):
            logger.info(f"Пользователь {chat_id} начал работу с ботом")
        elif text.startswith("/help"):
            logger.info(f"Пользователь {chat_id} запросил помощь")
        else:
            logger.info(f"Сообщение от {chat_id}: {text}")
    return {"status": "ok"} 