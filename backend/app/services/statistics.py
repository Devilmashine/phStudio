from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional, Union
import logging

from app.models.booking import Booking
from app.schemas.booking import Booking as BookingSchema

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for generating booking statistics and analytics"""
    
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_daily_stats(self, target_date: date) -> Dict[str, Union[int, float, Dict, List]]:
        """Get comprehensive statistics for a specific date
        
        Args:
            target_date: The date to generate statistics for
            
        Returns:
            Dictionary containing daily statistics
            
        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            bookings = (
                self.db.query(Booking)
                .filter(func.date(Booking.date) == target_date)
                .all()
            )

            total_bookings = len(bookings)
            total_hours = sum(
                (booking.end_time - booking.start_time).total_seconds() / 3600
                for booking in bookings
            )
            total_revenue = sum(booking.total_price for booking in bookings)

            time_distribution = self._get_time_distribution(bookings)
            avg_duration = total_hours / total_bookings if total_bookings > 0 else 0.0

            success_rate = (
                len([b for b in bookings if b.status == "completed"]) / total_bookings
                if total_bookings > 0
                else 0.0
            )
            cancellation_rate = (
                len([b for b in bookings if b.status == "cancelled"]) / total_bookings
                if total_bookings > 0
                else 0.0
            )

            popular_slots = self._get_popular_slots(bookings)
            new_vs_returning = self._get_new_vs_returning(bookings)
            notification_stats = self._get_notification_stats(bookings)

            return {
                "date": target_date.isoformat(),
                "total_bookings": total_bookings,
                "total_hours": round(total_hours, 2),
                "total_revenue": round(total_revenue, 2),
                "time_distribution": time_distribution,
                "average_duration": round(avg_duration, 2),
                "success_rate": round(success_rate, 3),
                "cancellation_rate": round(cancellation_rate, 3),
                "popular_slots": popular_slots,
                "new_vs_returning": new_vs_returning,
                "notification_stats": notification_stats,
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_daily_stats: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_daily_stats: {e}")
            raise

    async def get_weekly_stats(self, start_date: date) -> Dict[str, Any]:
        """Получение статистики за неделю"""
        end_date = start_date + timedelta(days=6)
        daily_stats = []

        for day in range(7):
            current_date = start_date + timedelta(days=day)
            stats = await self.get_daily_stats(current_date)
            daily_stats.append(stats)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "daily_stats": daily_stats,
            "total_bookings": sum(day["total_bookings"] for day in daily_stats),
            "total_hours": sum(day["total_hours"] for day in daily_stats),
            "total_revenue": sum(day["total_revenue"] for day in daily_stats),
        }

    async def get_monthly_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Получение статистики за месяц"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        bookings = (
            self.db.query(Booking)
            .filter(and_(Booking.date >= start_date, Booking.date <= end_date))
            .all()
        )

        total_bookings = len(bookings)
        total_hours = sum(
            (booking.end_time - booking.start_time).total_seconds() / 3600
            for booking in bookings
        )
        total_revenue = sum(booking.total_price for booking in bookings)

        return {
            "year": year,
            "month": month,
            "total_bookings": total_bookings,
            "total_hours": total_hours,
            "total_revenue": total_revenue,
            "average_daily_bookings": total_bookings / end_date.day,
            "average_daily_hours": total_hours / end_date.day,
            "average_daily_revenue": total_revenue / end_date.day,
        }

    def _get_time_distribution(self, bookings: List[Booking]) -> Dict[str, int]:
        """Распределение бронирований по времени суток"""
        distribution = {"morning": 0, "afternoon": 0, "evening": 0}
        for booking in bookings:
            hour = booking.start_time.hour
            if 6 <= hour < 12:
                distribution["morning"] += 1
            elif 12 <= hour < 18:
                distribution["afternoon"] += 1
            else:
                distribution["evening"] += 1
        return distribution

    def _get_popular_slots(self, bookings: List[Booking]) -> List[Dict[str, Any]]:
        """Популярные временные слоты"""
        slots = {}
        for booking in bookings:
            slot = f"{booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')}"
            slots[slot] = slots.get(slot, 0) + 1

        return [
            {"slot": slot, "count": count}
            for slot, count in sorted(slots.items(), key=lambda x: x[1], reverse=True)
        ]

    def _get_new_vs_returning(self, bookings: List[Booking]) -> Dict[str, int]:
        """Статистика новых и постоянных клиентов"""
        clients = {}
        for booking in bookings:
            if booking.client_email:
                clients[booking.client_email] = clients.get(booking.client_email, 0) + 1

        new = len([email for email, count in clients.items() if count == 1])
        returning = len([email for email, count in clients.items() if count > 1])

        return {"new": new, "returning": returning}

    def _get_notification_stats(self, bookings: List[Booking]) -> Dict[str, int]:
        """Статистика уведомлений"""
        return {
            "total_sent": len([b for b in bookings if b.notification_sent]),
            "total_pending": len([b for b in bookings if not b.notification_sent]),
        }
