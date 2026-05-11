import requests
import json

base_url = "http://127.0.0.1:8000"

def test_flow():
    # 1. Login to get token
    print("Testing Login...")
    login_payload = {"username": "superadmin", "password": "admin123"}
    try:
        resp = requests.post(f"{base_url}/auth/login", json=login_payload)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        
        data = resp.json()
        token = data["access_token"]
        print("Login successful. Token obtained.")
        
        # 2. Test protected endpoint (GET /users/)
        print("\nTesting Protected Endpoint (GET /users/)...")
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{base_url}/users/", headers=headers)
        
        if resp.status_code == 200:
            print("SUCCESS: Protected endpoint accessible!")
            print(f"Users found: {len(resp.json())}")
        else:
            print(f"FAILED: Protected endpoint returned {resp.status_code}")
            print(resp.text)
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_flow()
