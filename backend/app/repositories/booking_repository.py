"""
Enhanced Booking Repository with optimized queries and caching.

This module provides a production-grade repository for booking data access
with performance optimization, caching, and comprehensive query capabilities.
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from decimal import Decimal
from sqlalchemy import (
    select, and_, or_, func, desc, asc, text,
    extract, case, cast, Integer, String
)
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import SQLAlchemyError

from ..models.booking_enhanced import Booking, BookingState, SpaceType, PaymentStatus
from ..models.base_enhanced import BaseEnhanced
from ..core.result import Result, success, failure, DomainError


class RepositoryError(DomainError):
    """Base class for repository errors."""
    pass


class DatabaseConnectionError(RepositoryError):
    """Error raised when database connection fails."""
    
    def __init__(self, message: str):
        super().__init__(message, code="DATABASE_CONNECTION_ERROR")


class QueryExecutionError(RepositoryError):
    """Error raised when query execution fails."""
    
    def __init__(self, message: str):
        super().__init__(message, code="QUERY_EXECUTION_ERROR")


class BookingRepository:
    """
    Enhanced Booking Repository with comprehensive data access capabilities.
    
    This repository implements optimized queries, caching strategies, and
    performance optimizations for production-scale booking systems.
    """
    
    def __init__(self, db_session: Session, cache_service: Optional[Any] = None):
        self.db = db_session
        self.cache = cache_service
        self._query_cache = {}  # In-memory query cache
        self._cache_ttl = 300  # 5 minutes default TTL
    
    # Basic CRUD operations
    def create(self, booking: Booking) -> Result[Booking, RepositoryError]:
        """Create a new booking."""
        try:
            self.db.add(booking)
            self.db.commit()
            self.db.refresh(booking)
            
            # Invalidate relevant caches
            self._invalidate_booking_caches(booking)
            
            return success(booking)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            return failure(
                QueryExecutionError(f"Failed to create booking: {str(e)}")
            )
        except Exception as e:
            self.db.rollback()
            return failure(
                RepositoryError(f"Unexpected error creating booking: {str(e)}")
            )
    
    def get_by_id(self, booking_id: int) -> Result[Optional[Booking], RepositoryError]:
        """Get booking by ID with caching."""
        try:
            # Try cache first
            cache_key = f"booking:{booking_id}"
            if self.cache:
                cached_booking = self.cache.get(cache_key)
                if cached_booking:
                    return success(cached_booking)
            
            # Query database
            query = select(Booking).where(
                and_(
                    Booking.id == booking_id,
                    Booking.is_deleted == False
                )
            ).options(
                selectinload(Booking.calendar_event),
                selectinload(Booking.created_by_employee),
                selectinload(Booking.updated_by_employee)
            )
            
            result = self.db.execute(query)
            booking = result.scalar_one_or_none()
            
            # Cache result
            if booking and self.cache:
                self.cache.set(cache_key, booking, ttl=self._cache_ttl)
            
            return success(booking)
            
        except SQLAlchemyError as e:
            return failure(
                QueryExecutionError(f"Failed to get booking by ID: {str(e)}")
            )
        except Exception as e:
            return failure(
                RepositoryError(f"Unexpected error getting booking: {str(e)}")
            )
    
    def get_by_reference(self, reference: str) -> Result[Optional[Booking], RepositoryError]:
        """Get booking by reference number."""
        try:
            query = select(Booking).where(
                and_(
                    Booking.booking_reference == reference,
                    Booking.is_deleted == False
                )
            ).options(
                selectinload(Booking.created_by_employee),
                selectinload(Booking.updated_by_employee)
            )
            
            result = self.db.execute(query)
            booking = result.scalar_one_or_none()
            
            return success(booking)
            
        except SQLAlchemyError as e:
            return failure(
                QueryExecutionError(f"Failed to get booking by reference: {str(e)}")
            )

    def update(self, booking: Booking) -> Result[Booking, RepositoryError]:
        """Update an existing booking."""
        try:
            # Increment version for optimistic locking
            booking.version += 1
            
            self.db.commit()
            self.db.refresh(booking)
            
            # Invalidate relevant caches
            self._invalidate_booking_caches(booking)
            
            return success(booking)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            return failure(
                QueryExecutionError(f"Failed to update booking: {str(e)}")
            )
    
    def delete(self, booking_id: int, user_id: int) -> Result[bool, RepositoryError]:
        """Soft delete a booking."""
        try:
            # Get booking
            booking_result = self.get_by_id(booking_id)
            if booking_result.is_failure():
                return booking_result
            
            booking = booking_result.value
            if not booking:
                return failure(
                    RepositoryError(f"Booking {booking_id} not found")
                )
            
            # Soft delete
            booking.soft_delete(user_id)
            
            # Save changes
            self.db.commit()
            
            # Invalidate caches
            self._invalidate_booking_caches(booking)
            
            return success(True)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            return failure(
                QueryExecutionError(f"Failed to delete booking: {str(e)}")
            )
    
    # Advanced query methods
    def find_by_filters(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> Result[List[Booking], RepositoryError]:
        """
        Find bookings with advanced filtering and pagination.
        
        Args:
            filters: Dictionary of filters to apply
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            
        Returns:
            Result containing list of bookings or error
        """
        try:
            # Build base query
            query = select(Booking).where(Booking.is_deleted == False)
            
            # Apply filters
            query = self._apply_filters(query, filters)
            
            # Apply ordering
            if order_by:
                query = self._apply_ordering(query, order_by, order_direction)
            
            # Apply pagination
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            # Execute query
            result = self.db.execute(query)
            bookings = result.scalars().all()
            
            return success(bookings)
            
        except SQLAlchemyError as e:
            return failure(
                QueryExecutionError(f"Failed to find bookings: {str(e)}")
            )
    
    def find_conflicting_bookings(
        self,
        start_time: datetime,
        end_time: datetime,
        space_type: SpaceType,
        exclude_booking_id: Optional[int] = None
    ) -> Result[List[Booking], RepositoryError]:
        """Find bookings that conflict with the given time slot."""
        try:
            query = select(Booking).where(
                and_(
                    Booking.is_deleted == False,
                    Booking.space_type == space_type,
                    Booking.state.in_([
                        BookingState.CONFIRMED,
                        BookingState.IN_PROGRESS
                    ]),
                    or_(
                        # New booking starts during existing booking
                        and_(
                            start_time >= Booking.start_time,
                            start_time < Booking.end_time
                        ),
                        # New booking ends during existing booking
                        and_(
                            end_time > Booking.start_time,
                            end_time <= Booking.end_time
                        ),
                        # New booking completely contains existing booking
                        and_(
                            start_time <= Booking.start_time,
                            end_time >= Booking.end_time
                        )
                    )
                )
            )
            
            # Exclude specific booking if provided
            if exclude_booking_id:
                query = query.where(Booking.id != exclude_booking_id)
            
            result = self.db.execute(query)
            conflicting_bookings = result.scalars().all()
            
            return success(conflicting_bookings)
            
        except SQLAlchemyError as e:
            return failure(
                QueryExecutionError(f"Failed to find conflicting bookings: {str(e)}")
            )
    
    def find_bookings_for_date_range(
        self,
        start_date: date,
        end_date: date,
        space_type: Optional[SpaceType] = None,
        state: Optional[BookingState] = None
    ) -> Result[List[Booking], RepositoryError]:
        """Find bookings in a date range with optional filtering."""
        try:
            filters = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            if space_type:
                filters["space_type"] = space_type
            if state:
                filters["state"] = state
            
            return self.find_by_filters(filters)
            
        except Exception as e:
            return failure(
                RepositoryError(f"Failed to find bookings for date range: {str(e)}")
            )
    
    def find_upcoming_bookings(
        self,
        limit: int = 50,
        include_cancelled: bool = False
    ) -> Result[List[Booking], RepositoryError]:
        """Find upcoming bookings."""
        try:
            now = datetime.now()
            
            filters = {
                "start_time": now,
                "start_direction": "gte"  # Custom filter for >=
            }
            
            if not include_cancelled:
                filters["state"] = [BookingState.PENDING, BookingState.CONFIRMED, BookingState.IN_PROGRESS]
            
            return self.find_by_filters(
                filters,
                limit=limit,
                order_by="start_time",
                order_direction="asc"
            )
            
        except Exception as e:
            return failure(
                RepositoryError(f"Failed to find upcoming bookings: {str(e)}")
            )
    
    def find_overdue_bookings(self) -> Result[List[Booking], RepositoryError]:
        """Find overdue bookings (in progress but past end time)."""
        try:
            now = datetime.now()
            
            query = select(Booking).where(
                and_(
                    Booking.is_deleted == False,
                    Booking.state == BookingState.IN_PROGRESS,
                    Booking.end_time < now
                )
            ).order_by(Booking.end_time.asc())
            
            result = self.db.execute(query)
            overdue_bookings = result.scalars().all()
            
            return success(overdue_bookings)
            
        except SQLAlchemyError as e:
            return failure(
                QueryExecutionError(f"Failed to find overdue bookings: {str(e)}")
            )
    
    def get_revenue_analytics(
        self,
        start_date: date,
        end_date: date,
        group_by: Optional[str] = None
    ) -> Result[Dict[str, Any], RepositoryError]:
        """Get revenue analytics for a date range."""
        try:
            # Base revenue query
            revenue_query = select(
                func.date(Booking.booking_date).label("date"),
                func.sum(Booking.total_price).label("revenue"),
                func.count(Booking.id).label("booking_count")
            ).where(
                and_(
                    Booking.is_deleted == False,
                    Booking.booking_date >= start_date,
                    Booking.booking_date <= end_date,
                    Booking.state.in_([BookingState.CONFIRMED, BookingState.COMPLETED])
                )
            ).group_by(func.date(Booking.booking_date)).order_by(func.date(Booking.booking_date))
            
            result = self.db.execute(revenue_query)
            revenue_data = result.fetchall()
            
            # Prepare result
            analytics_data = {
                "daily_revenue": [
                    {
                        "date": row.date.isoformat(),
                        "revenue": float(row.revenue or 0),
                        "booking_count": row.booking_count
                    }
                    for row in revenue_data
                ]
            }
            
            return success(analytics_data)
            
        except SQLAlchemyError as e:
            return failure(
                QueryExecutionError(f"Failed to get revenue analytics: {str(e)}")
            )
    
    def get_booking_stats(
        self,
        start_date: date,
        end_date: date,
        group_by: Optional[str] = None
    ) -> Result[Dict[str, Any], RepositoryError]:
        """Get booking statistics for a date range."""
        try:
            # Base query for stats
            base_query = select(
                func.count(Booking.id).label("total_bookings"),
                func.sum(Booking.total_price).label("total_revenue"),
                func.avg(Booking.duration_hours).label("avg_duration"),
                func.sum(case(
                    (Booking.state == BookingState.COMPLETED, 1),
                    else_=0
                )).label("completed_bookings"),
                func.sum(case(
                    (Booking.state == BookingState.CANCELLED, 1),
                    else_=0
                )).label("cancelled_bookings")
            ).where(
                and_(
                    Booking.is_deleted == False,
                    Booking.booking_date >= start_date,
                    Booking.booking_date <= end_date
                )
            )
            
            # Execute base stats query
            result = self.db.execute(base_query)
            stats = result.fetchone()
            
            # Prepare result
            result_data = {
                "total_bookings": stats.total_bookings or 0,
                "total_revenue": float(stats.total_revenue or 0),
                "avg_duration": float(stats.avg_duration or 0),
                "completed_bookings": stats.completed_bookings or 0,
                "cancelled_bookings": stats.cancelled_bookings or 0,
                "completion_rate": 0,
                "cancellation_rate": 0
            }
            
            # Calculate rates
            if result_data["total_bookings"] > 0:
                result_data["completion_rate"] = (
                    result_data["completed_bookings"] / result_data["total_bookings"]
                ) * 100
                result_data["cancellation_rate"] = (
                    result_data["cancelled_bookings"] / result_data["total_bookings"]
                ) * 100
            
            # Group by specific field if requested
            if group_by and group_by in ["date", "space_type", "state"]:
                grouped_stats = self._get_grouped_stats(start_date, end_date, group_by)
                result_data["grouped_stats"] = grouped_stats
            
            return success(result_data)
            
        except SQLAlchemyError as e:
            return failure(
                QueryExecutionError(f"Failed to get booking stats: {str(e)}")
            )
    
    def get_bookings_with_optimized_loading(
        self,
        filters: Dict[str, Any],
        load_relationships: bool = True
    ) -> Result[List[Booking], RepositoryError]:
        """Get bookings with optimized relationship loading."""
        try:
            query = select(Booking).where(Booking.is_deleted == False)
            
            # Apply filters
            query = self._apply_filters(query, filters)
            
            # Optimize relationship loading
            if load_relationships:
                query = query.options(
                    selectinload(Booking.created_by_employee),
                    selectinload(Booking.updated_by_employee)
                )
            
            result = self.db.execute(query)
            bookings = result.scalars().all()
            
            return success(bookings)
            
        except SQLAlchemyError as e:
            return failure(
                QueryExecutionError(f"Failed to get bookings with optimized loading: {str(e)}")
            )
    
    def bulk_update_bookings(
        self,
        booking_ids: List[int],
        update_data: Dict[str, Any],
        user_id: int
    ) -> Result[int, RepositoryError]:
        """Bulk update multiple bookings."""
        try:
            # Get bookings to update
            query = select(Booking).where(
                and_(
                    Booking.id.in_(booking_ids),
                    Booking.is_deleted == False
                )
            )
            
            result = self.db.execute(query)
            bookings = result.scalars().all()
            
            updated_count = 0
            for booking in bookings:
                # Apply updates
                for field, value in update_data.items():
                    if hasattr(booking, field):
                        setattr(booking, field, value)
                
                # Update audit trail
                booking.update_audit_trail(
                    "bulk_updated",
                    user_id=user_id,
                    details={"updated_fields": list(update_data.keys())}
                )
                
                # Increment version
                booking.increment_version()
                
                updated_count += 1
            
            # Commit all changes
            self.db.commit()
            
            # Invalidate caches for all updated bookings
            for booking in bookings:
                self._invalidate_booking_caches(booking)
            
            return success(updated_count)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            return failure(
                QueryExecutionError(f"Failed to bulk update bookings: {str(e)}")
            )

    # Private helper methods
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query."""
        for field, value in filters.items():
            if value is None:
                continue
            
            if field == "start_date":
                query = query.where(Booking.booking_date >= value)
            elif field == "end_date":
                query = query.where(Booking.booking_date <= value)
            elif field == "start_time":
                if filters.get("start_direction") == "gte":
                    query = query.where(Booking.start_time >= value)
                else:
                    query = query.where(Booking.start_time == value)
            elif field == "end_time":
                query = query.where(Booking.end_time == value)
            elif field == "space_type":
                query = query.where(Booking.space_type == value)
            elif field == "state":
                if isinstance(value, list):
                    query = query.where(Booking.state.in_(value))
                else:
                    query = query.where(Booking.state == value)
            elif field == "client_name":
                query = query.where(Booking.client_name.ilike(f"%{value}%"))
            elif field == "client_phone":
                query = query.where(Booking.client_phone.ilike(f"%{value}%"))
            elif field == "payment_status":
                query = query.where(Booking.payment_status == value)
            elif field == "source":
                query = query.where(Booking.source == value)
            elif field == "priority":
                query = query.where(Booking.priority == value)
            elif field == "created_by":
                query = query.where(Booking.created_by == value)
            elif field == "updated_by":
                query = query.where(Booking.updated_by == value)
        
        return query
    
    def _apply_ordering(self, query, order_by: str, order_direction: str = "asc"):
        """Apply ordering to query."""
        if hasattr(Booking, order_by):
            field = getattr(Booking, order_by)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(field))
            else:
                query = query.order_by(asc(field))
        
        return query
    
    def _get_grouped_stats(
        self,
        start_date: date,
        end_date: date,
        group_by: str
    ) -> Dict[str, Any]:
        """Get grouped statistics."""
        try:
            if group_by == "date":
                group_field = func.date(Booking.booking_date)
            elif group_by == "space_type":
                group_field = Booking.space_type
            elif group_by == "state":
                group_field = Booking.state
            else:
                return {}
            
            query = select(
                group_field.label("group_value"),
                func.count(Booking.id).label("count"),
                func.sum(Booking.total_price).label("revenue")
            ).where(
                and_(
                    Booking.is_deleted == False,
                    Booking.booking_date >= start_date,
                    Booking.booking_date <= end_date
                )
            ).group_by(group_field).order_by(group_field)
            
            result = self.db.execute(query)
            grouped_stats = {}
            
            for row in result.fetchall():
                group_value = row.group_value
                if hasattr(group_value, 'value'):  # Enum
                    group_value = group_value.value
                elif hasattr(group_value, 'isoformat'):  # Date
                    group_value = group_value.isoformat()
                
                grouped_stats[str(group_value)] = {
                    "count": row.count or 0,
                    "revenue": float(row.revenue or 0)
                }
            
            return grouped_stats
            
        except SQLAlchemyError:
            return {}
    
    def _invalidate_booking_caches(self, booking: Booking) -> None:
        """Invalidate caches related to a booking."""
        if not self.cache:
            return
        
        # Invalidate specific booking cache
        cache_keys = [
            f"booking:{booking.id}",
            f"bookings:date:{booking.booking_date}",
            f"bookings:space:{booking.space_type.value}:{booking.booking_date}",
            f"bookings:state:{booking.state.value}",
        ]
        
        for key in cache_keys:
            self.cache.delete(key)
    
    # Cache management methods
    def clear_all_caches(self) -> None:
        """Clear all booking-related caches."""
        if not self.cache:
            return
        
        # Clear in-memory cache
        self._query_cache.clear()
        
        # Clear external cache (implementation depends on cache service)
        # This is a placeholder for actual cache clearing logic
        pass
    
    def warm_cache_for_date(self, target_date: date) -> None:
        """Warm cache for a specific date."""
        if not self.cache:
            return
        
        try:
            # Get bookings for the date
            filters = {"start_date": target_date, "end_date": target_date}
            bookings_result = self.find_by_filters(filters)
            
            if bookings_result.is_success():
                bookings = bookings_result.value
                
                # Cache the results
                cache_key = f"bookings:date:{target_date}"
                self.cache.set(cache_key, bookings, ttl=self._cache_ttl)
                
        except Exception:
            # Cache warming failed, but don't fail the operation
            pass