import requests
import json

# Authenticate and get token
auth_url = "http://localhost:8888/api/auth/token"
auth_data = {
    "username": "testadmin",
    "password": "SecurePass123!"
}

print("Authenticating...")
response = requests.post(auth_url, data=auth_data)
print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get("access_token")
    print(f"Access token: {access_token}")
    
    # Create a booking
    booking_url = "http://localhost:8888/api/bookings/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    booking_data = {
        "client_name": "Test User",
        "client_phone": "+79998887766",
        "date": "2025-09-01",
        "start_time": "10:00",
        "end_time": "11:00",
        "total_price": 1000,
        "people_count": 1,
        "notes": "Test booking for Telegram notification"
    }
    
    print("Creating booking...")
    booking_response = requests.post(booking_url, headers=headers, json=booking_data)
    print(f"Booking status code: {booking_response.status_code}")
    print(f"Booking response: {booking_response.text}")
else:
    print("Authentication failed")