import requests
import json

BASE_URL = "http://localhost:8000"
# Use credentials from your seeding script
USERNAME = "user_1"
PASSWORD = "password123"

def verify_gzip():
    print("🚀 Verifying Gzip Compression on /tasks/ endpoint...")

    # 1. Get Token
    login_data = {"username": USERNAME, "password": PASSWORD}
    login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_resp.status_code != 200:
        print("❌ Login failed. Make sure you ran the seeding script first.")
        return

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Request WITH Gzip
    # 'requests' sends Accept-Encoding: gzip by default, but we'll be explicit
    gzip_headers = {**headers, "Accept-Encoding": "gzip"}
    resp_gzip = requests.get(f"{BASE_URL}/tasks/", headers=gzip_headers, params={"limit": 50})

    # 3. Request WITHOUT Gzip (Identity)
    # We force the server to send uncompressed data for comparison
    identity_headers = {**headers, "Accept-Encoding": "identity"}
    resp_raw = requests.get(f"{BASE_URL}/tasks/", headers=identity_headers, params={"limit": 50})

    # --- Analysis ---
    
    # Actual Size: The size of the JSON data after decompression (what the app sees)
    actual_size = len(resp_raw.content)
    
    # Transferred Size: The size of the bytes sent over the network
    # For a gzipped response, requests decompresses automatically, so we look 
    # at the Content-Length header or the raw stream to find transferred size.
    transferred_size = int(resp_gzip.headers.get("Content-Length", 0))
    
    # If Content-Length is missing (common with chunked encoding), 
    # we can calculate the compression ratio manually for the demo
    encoding = resp_gzip.headers.get("Content-Encoding", "None")
    
    print("\n" + "="*40)
    print(f"📊 COMPRESSION REPORT for {len(resp_gzip.json())} tasks")
    print("="*40)
    print(f"Endpoint:         /tasks/?limit=50")
    print(f"Content-Encoding: {encoding}")
    print(f"Actual Size:      {actual_size / 1024:.2f} KB ({actual_size} bytes)")
    
    if encoding == "gzip":
        # Note: If transferred_size is 0 due to streaming, we use a fallback to show the diff
        if transferred_size == 0:
            # Fallback for local testing if server doesn't provide Content-Length
            import zlib
            transferred_size = len(zlib.compress(resp_raw.content))
            print(f"Transferred Size: {transferred_size / 1024:.2f} KB (Simulated)")
        else:
            print(f"Transferred Size: {transferred_size / 1024:.2f} KB (From Header)")
            
        savings = (1 - (transferred_size / actual_size)) * 100
        print(f"Bandwidth Saved:  {savings:.1f}% ✅")
    else:
        print("❌ Gzip was NOT applied (Check minimum_size setting in main.py)")
    
    print("="*40)

if __name__ == "__main__":
    verify_gzip()