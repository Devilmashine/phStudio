#!/bin/bash
# Получить список бронирований на сегодня
DATE=$(date +%F)
echo "\n== GET /api/v1/bookings/?date=$DATE ==\n"
curl -s "http://localhost:8000/api/v1/bookings/?date=$DATE" | jq '.'

# Получить все бронирования без фильтра
echo "\n== GET /api/v1/bookings/ ==\n"
curl -s "http://localhost:8000/api/v1/bookings/" | jq '.'
