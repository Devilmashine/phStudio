import requests
import time

def test_backend():
    """Test if the backend is running"""
    try:
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Test the health endpoint
        response = requests.get("http://localhost:8888/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

if __name__ == "__main__":
    test_backend()