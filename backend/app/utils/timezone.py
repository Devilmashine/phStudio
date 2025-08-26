"""
Utilities for handling Moscow timezone (UTC+3) operations
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import pytz

# Moscow timezone
MOSCOW_TZ = pytz.timezone('Europe/Moscow')
MOSCOW_OFFSET = timedelta(hours=3)


def get_moscow_now() -> datetime:
    """Get current time in Moscow timezone"""
    return datetime.now(MOSCOW_TZ)


def to_moscow_time(dt: datetime) -> datetime:
    """Convert datetime to Moscow timezone"""
    if dt is None:
        raise ValueError("datetime cannot be None")
        
    if dt.tzinfo is None:
        # Assume naive datetime is in Moscow time
        return MOSCOW_TZ.localize(dt)
    return dt.astimezone(MOSCOW_TZ)


def from_moscow_time(dt: datetime) -> datetime:
    """Convert Moscow time to UTC for database storage"""
    if dt.tzinfo is None:
        # Assume naive datetime is in Moscow time
        moscow_dt = MOSCOW_TZ.localize(dt)
    else:
        moscow_dt = dt.astimezone(MOSCOW_TZ)
    
    return moscow_dt.astimezone(timezone.utc)


def parse_moscow_datetime(date_str: str) -> datetime:
    """
    Parse datetime string as Moscow time
    Handles formats like:
    - 2025-08-28T10:00:00+03:00
    - 2025-08-28T10:00:00
    """
    if date_str.endswith('+03:00'):
        # Already has Moscow timezone
        return datetime.fromisoformat(date_str.replace('+03:00', '')).replace(tzinfo=MOSCOW_TZ)
    elif 'T' in date_str:
        # ISO format without timezone - assume Moscow time
        dt = datetime.fromisoformat(date_str)
        return MOSCOW_TZ.localize(dt)
    else:
        # Date only - assume midnight Moscow time
        dt = datetime.fromisoformat(date_str + 'T00:00:00')
        return MOSCOW_TZ.localize(dt)


def format_moscow_datetime(dt: datetime) -> str:
    """Format datetime in Moscow timezone as ISO string with +03:00 offset"""
    moscow_dt = to_moscow_time(dt)
    return moscow_dt.strftime('%Y-%m-%dT%H:%M:%S+03:00')


def is_same_moscow_date(dt1: datetime, dt2: datetime) -> bool:
    """Check if two datetimes are on the same date in Moscow timezone"""
    moscow_dt1 = to_moscow_time(dt1)
    moscow_dt2 = to_moscow_time(dt2)
    return moscow_dt1.date() == moscow_dt2.date()


def get_moscow_date_range(date_str: str):
    """
    Get start and end of day in Moscow timezone for a given date
    Returns tuple of (start_datetime, end_datetime) in UTC for database queries
    """
    # Parse date string as Moscow date
    if 'T' in date_str:
        date_only = date_str.split('T')[0]
    else:
        date_only = date_str
    
    # Create start of day in Moscow time
    moscow_start = MOSCOW_TZ.localize(
        datetime.fromisoformat(date_only + 'T00:00:00')
    )
    moscow_end = MOSCOW_TZ.localize(
        datetime.fromisoformat(date_only + 'T23:59:59')
    )
    
    # Convert to UTC for database queries
    utc_start = moscow_start.astimezone(timezone.utc)
    utc_end = moscow_end.astimezone(timezone.utc)
    
    return utc_start, utc_end