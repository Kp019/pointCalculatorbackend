import requests
import sys
import time
import random
import string

BASE_URL = "http://localhost:8001/api/v1"

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def test_auth_flow():
    print("Starting Auth Flow Verification...")
    
    # Generate random user credentials
    email = f"test.user.{generate_random_string().lower()}@gmail.com"
    password = "TestPassword123!"  # Stronger password just in case
    username = f"user_{generate_random_string()}"
    
    print(f"Testing with Email: {email}")
    
    # 1. Signup
    print("\n1. Testing Signup...")
    signup_data = {
        "email": email,
        "password": password,
        "username": username
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if response.status_code == 201:
            print("Signup Successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"Signup Failed! Status: {response.status_code}, Response: {response.text}")
            # If signup fails (e.g. email confirm required), we might need to handle that.
            # But Supabase usually allows login if confirm is disabled, or returns session.
            # If confirm is enabled, we can't fully test without email access.
            # Assuming development mode or email confirm disabled for now.
    except Exception as e:
        print(f"Signup Exception: {e}")
        return

    # 2. Login
    print("\n2. Testing Login...")
    login_data = {
        "email": email,
        "password": password
    }
    token = None
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("Login Successful!")
            data = response.json()
            token = data["access_token"]
            print(f"Token received (truncated): {token[:20]}...")
            
            # Verify user profile in response
            if data["user"]["username"] == username:
                print("User profile verify: Username matches.")
            else:
                print(f"User profile verify: Username mismatch! Got {data['user']['username']}")
        else:
            print(f"Login Failed! Status: {response.status_code}, Response: {response.text}")
            return
    except Exception as e:
        print(f"Login Exception: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Game (Protected Endpoint)
    print("\n3. Testing Create Game (Protected)...")
    game_data = {
        "name": "Test Game",
        "description": "A test game for auth verification",
        "rules": {"test": "rule"}
    }
    game_id = None
    try:
        response = requests.post(f"{BASE_URL}/games/", json=game_data, headers=headers)
        if response.status_code == 200:
            print("Create Game Successful!")
            data = response.json()
            game_id = data["id"]
            print(f"Game ID: {game_id}")
            if data.get("user_id"):
                 print(f"Game user_id set correctly: {data['user_id']}")
            else:
                 print("WARNING: user_id not returned in game object")
        else:
            print(f"Create Game Failed! Status: {response.status_code}, Response: {response.text}")
            return
    except Exception as e:
        print(f"Create Game Exception: {e}")
        return

    # 4. Get Games (Protected Endpoint - Should see the game)
    print("\n4. Testing Get Games (Protected)...")
    try:
        response = requests.get(f"{BASE_URL}/games/", headers=headers)
        if response.status_code == 200:
            games = response.json()
            print(f"Get Games Successful! Found {len(games)} games.")
            found = False
            for g in games:
                if g["id"] == game_id:
                    found = True
                    break
            if found:
                print("Verified: Created game is in the list.")
            else:
                print("FAILED: Created game NOT found in list.")
        else:
            print(f"Get Games Failed! Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Get Games Exception: {e}")

    # 5. Test Unauthorized Access
    print("\n5. Testing Unauthorized Access (Should Fail)...")
    try:
        # Try to get games without header
        response = requests.get(f"{BASE_URL}/games/")
        if response.status_code == 401 or response.status_code == 403:
            print(f"Unauthorized Access Blocked as expected. Status: {response.status_code}")
        else:
            print(f"WARNING: Unauthorized access NOT blocked! Status: {response.status_code}")
            
    except Exception as e:
        print(f"Unauthorized Access Exception: {e}")

if __name__ == "__main__":
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the backend.")
        print("Make sure the FastAPI server is running on localhost:8000")
