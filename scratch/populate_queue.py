import requests
import time

BASE_URL = "http://localhost:7860"

# Fill active slots (max 2)
for i in range(2):
    uid = f"dummy_active_{i}"
    requests.get(f"{BASE_URL}/queue/status/{uid}")

# Fill waiting queue (9 users ahead)
for i in range(9):
    uid = f"dummy_wait_{i}"
    res = requests.get(f"{BASE_URL}/queue/status/{uid}")
    print(f"User {uid} status: {res.json()}")

print("Waitlist populated.")
