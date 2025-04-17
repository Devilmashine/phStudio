from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict, Any

from app.services.statistics import StatisticsService
from app.core.database import get_db

router = APIRouter(prefix="/stats", tags=["statistics"])

@router.get("/daily/{target_date}", response_model=Dict[str, Any])
async def get_daily_stats(
    target_date: date,
    db: Session = Depends(get_db)
):
    """Получение статистики за конкретный день"""
    try:
        stats_service = StatisticsService(db)
        return stats_service.get_daily_stats(target_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly/{start_date}", response_model=List[Dict[str, Any]])
async def get_weekly_stats(
    start_date: date,
    db: Session = Depends(get_db)
):
    """Получение статистики за неделю"""
    try:
        stats_service = StatisticsService(db)
        return stats_service.get_weekly_stats(start_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly/{year}/{month}", response_model=Dict[str, Any])
async def get_monthly_stats(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Получение статистики за месяц"""
    try:
        stats_service = StatisticsService(db)
        return stats_service.get_monthly_stats(year, month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 