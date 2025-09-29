import os
import sys
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

engine = create_engine(DB_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, booking_reference, booking_date, start_time, end_time, state, client_name, client_phone
        FROM bookings
        ORDER BY booking_date, start_time
    """))
    print("id | booking_reference | booking_date | start_time | end_time | state | client_name | client_phone")
    for row in result:
        print(" | ".join(str(x) for x in row))
