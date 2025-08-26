from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.statistics import DailyStats
from app.models.booking import Booking
from app.models.calendar import CalendarEvent
from typing import List, Dict, Any

class StatisticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_stats(self, target_date: date) -> Dict[str, Any]:
        """Получение статистики за конкретный день"""
        stats = self.db.query(DailyStats).filter(DailyStats.date == target_date).first()
        
        if not stats:
            # Если статистики нет, создаем новую запись
            stats = self._calculate_daily_stats(target_date)
            self.db.add(stats)
            self.db.commit()
            self.db.refresh(stats)
        
        return {
            "date": stats.date.isoformat(),
            "total_bookings": stats.total_bookings,
            "total_hours": stats.total_hours,
            "total_revenue": stats.total_revenue,
            "time_distribution": stats.time_distribution,
            "average_booking_duration": stats.average_booking_duration,
            "booking_success_rate": stats.booking_success_rate,
            "cancellation_rate": stats.cancellation_rate,
            "most_popular_slots": stats.most_popular_slots,
            "new_clients": stats.new_clients,
            "returning_clients": stats.returning_clients,
            "notifications_sent": stats.notifications_sent,
            "notifications_failed": stats.notifications_failed
        }

    def get_weekly_stats(self, start_date: date) -> List[Dict[str, Any]]:
        """Получение статистики за неделю"""
        end_date = start_date + timedelta(days=6)
        stats = self.db.query(DailyStats)\
            .filter(DailyStats.date >= start_date, DailyStats.date <= end_date)\
            .order_by(DailyStats.date)\
            .all()
        
        return [self.get_daily_stats(stat.date) for stat in stats]

    def get_monthly_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Получение статистики за месяц"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        stats = self.db.query(DailyStats)\
            .filter(DailyStats.date >= start_date, DailyStats.date <= end_date)\
            .all()
        
        # Агрегация данных за месяц
        monthly_stats = {
            "total_bookings": sum(stat.total_bookings for stat in stats),
            "total_hours": sum(stat.total_hours for stat in stats),
            "total_revenue": sum(stat.total_revenue for stat in stats),
            "average_booking_duration": sum(stat.average_booking_duration for stat in stats) / len(stats) if stats else 0,
            "booking_success_rate": sum(stat.booking_success_rate for stat in stats) / len(stats) if stats else 0,
            "cancellation_rate": sum(stat.cancellation_rate for stat in stats) / len(stats) if stats else 0,
            "new_clients": sum(stat.new_clients for stat in stats),
            "returning_clients": sum(stat.returning_clients for stat in stats),
            "notifications_sent": sum(stat.notifications_sent for stat in stats),
            "notifications_failed": sum(stat.notifications_failed for stat in stats)
        }
        
        return monthly_stats

    def _calculate_daily_stats(self, target_date: date) -> DailyStats:
        """Расчет статистики за день"""
        # Получаем все бронирования за день
        bookings = self.db.query(Booking)\
            .filter(func.date(Booking.start_time) == target_date)\
            .all()
        
        # Получаем все события календаря за день
        calendar_events = self.db.query(CalendarEvent)\
            .filter(func.date(CalendarEvent.start_time) == target_date)\
            .all()
        
        # Расчет основных метрик
        total_bookings = len(bookings)
        total_hours = sum((b.end_time - b.start_time).total_seconds() / 3600 for b in bookings)
        total_revenue = sum(b.total_price for b in bookings)
        
        # Расчет распределения по времени
        time_distribution = {}
        for hour in range(24):
            time_distribution[f"{hour:02d}:00"] = len([
                b for b in bookings 
                if b.start_time.hour <= hour < b.end_time.hour
            ])
        
        # Расчет средних значений
        average_booking_duration = total_hours / total_bookings if total_bookings > 0 else 0
        
        # Расчет процентов
        successful_bookings = len([b for b in bookings if b.status == "confirmed"])
        booking_success_rate = (successful_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        cancelled_bookings = len([b for b in bookings if b.status == "cancelled"])
        cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Создание объекта статистики
        stats = DailyStats(
            date=target_date,
            total_bookings=total_bookings,
            total_hours=total_hours,
            total_revenue=total_revenue,
            time_distribution=time_distribution,
            average_booking_duration=average_booking_duration,
            booking_success_rate=booking_success_rate,
            cancellation_rate=cancellation_rate,
            most_popular_slots=self._get_most_popular_slots(bookings),
            new_clients=self._count_new_clients(bookings),
            returning_clients=self._count_returning_clients(bookings),
            notifications_sent=self._count_notifications(calendar_events, "sent"),
            notifications_failed=self._count_notifications(calendar_events, "failed")
        )
        
        return stats

    def _get_most_popular_slots(self, bookings: List[Booking]) -> List[Dict[str, Any]]:
        """Получение самых популярных временных слотов"""
        slots = {}
        for booking in bookings:
            slot = f"{booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')}"
            slots[slot] = slots.get(slot, 0) + 1
        
        return [
            {"slot": slot, "count": count}
            for slot, count in sorted(slots.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

    def _count_new_clients(self, bookings: List[Booking]) -> int:
        """Подсчет новых клиентов"""
        client_phones = set()
        new_clients = 0
        
        for booking in bookings:
            if booking.client_phone not in client_phones:
                client_phones.add(booking.client_phone)
                new_clients += 1
        
        return new_clients

    def _count_returning_clients(self, bookings: List[Booking]) -> int:
        """Подсчет возвращающихся клиентов"""
        client_phones = set()
        returning_clients = 0
        
        for booking in bookings:
            if booking.client_phone in client_phones:
                returning_clients += 1
            else:
                client_phones.add(booking.client_phone)
        
        return returning_clients

    def _count_notifications(self, events: List[CalendarEvent], status: str) -> int:
        """Подсчет уведомлений по статусу"""
        return len([
            event for event in events
            if event.notification_status == status
        ]) 