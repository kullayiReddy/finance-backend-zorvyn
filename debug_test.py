import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Debug test - Check what's being sent
print("\n🔍 DEBUG: Password Encoding Test")
print("="*60)

password = "abc123"
print(f"Password String: {password}")
print(f"Password Length: {len(password)} characters")
print(f"Password Bytes: {password.encode('utf-8')}")
print(f"Password Bytes Length: {len(password.encode('utf-8'))} bytes")

# Try registration with debug printing
print("\n📤 Sending Registration Request")
data = {
    "email": "debug@test.com",
    "password": password,
    "full_name": "Debug User",
    "role": "viewer"
}

print(f"Request payload: {json.dumps(data, indent=2)}")
print(f"Password in payload: '{data['password']}' (length: {len(data['password'])})")

r = requests.post(f"{BASE_URL}/api/v1/auth/register", json=data)

print(f"\n📩 Response Status: {r.status_code}")
print(f"Response Body: {json.dumps(r.json(), indent=2)}")

if r.status_code != 201:
    print(f"\n❌ Registration failed!")
    print(f"Error Message: {r.json().get('message', 'Unknown error')}")
