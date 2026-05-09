import requests
import json

url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
api_url = "http://127.0.0.1:5000/api/download"

print(f"Testing download for {url}...")
try:
    response = requests.post(api_url, json={"url": url}, timeout=60, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
    if response.status_code == 200:
        print("Success! Download triggered.")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
    else:
        print(f"Failed! Status: {response.status_code}")
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
