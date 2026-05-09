import requests
import json

url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ" # Testing with a known good URL
api_url = "http://127.0.0.1:5000/api/info"

print(f"Testing info for {url}...")
try:
    response = requests.post(api_url, json={"url": url}, timeout=20)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
