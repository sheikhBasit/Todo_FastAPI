import requests
import time
import statistics

# BASE_URL = "http://localhost:8000"
BASE_URL = "https://todo-fast-api-alpha.vercel.app"
USERNAME = "user_1"
PASSWORD = "password123"
ITERATIONS = 50  # Number of times to hit the endpoint for a stable average

def benchmark():
    print(f"⏱️ Starting Speed Benchmark ({ITERATIONS} iterations per test)...")

    # 1. Get Authentication Token
    login_data = {"username": USERNAME, "password": PASSWORD}
    login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if login_resp.status_code != 200:
        print("❌ Login failed. Run the seed script first.")
        return
    
    token = login_resp.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    # 2. Benchmark WITHOUT Gzip (Identity)
    raw_times = []
    print("🏃 Testing WITHOUT Gzip...")
    for _ in range(ITERATIONS):
        start = time.perf_counter()
        requests.get(
            f"{BASE_URL}/tasks/", 
            headers={**auth_header, "Accept-Encoding": "identity"},
            params={"limit": 100}
        )
        raw_times.append(time.perf_counter() - start)

    # 3. Benchmark WITH Gzip
    gzip_times = []
    print("🚀 Testing WITH Gzip...")
    for _ in range(ITERATIONS):
        start = time.perf_counter()
        r = requests.get(
            f"{BASE_URL}/tasks/", 
            headers={**auth_header, "Accept-Encoding": "gzip"},
            params={"limit": 100}
        )
        gzip_times.append(time.perf_counter() - start)
        
        # Safety Check: Ensure Gzip was actually used
        if _ == 0 and r.headers.get("Content-Encoding") != "gzip":
            print("⚠️ WARNING: Server did NOT return Gzip. Payload might be too small for minimum_size.")

    # --- Calculation & Results ---
    avg_raw = statistics.mean(raw_times) * 1000  # Convert to ms
    avg_gzip = statistics.mean(gzip_times) * 1000
    
    diff = avg_raw - avg_gzip
    percent = (diff / avg_raw) * 100

    print("\n" + "="*45)
    print(f"🏁 BENCHMARK RESULTS (Average of {ITERATIONS} runs)")
    print("="*45)
    print(f"Without Gzip:  {avg_raw:.2f} ms")
    print(f"With Gzip:     {avg_gzip:.2f} ms")
    print("-"*45)
    
    if diff > 0:
        print(f"Result: Gzip is {percent:.1f}% FASTER ({diff:.2f} ms saved)")
    else:
        print(f"Result: Gzip is {abs(percent):.1f}% SLOWER on localhost")
        print("💡 Note: On localhost, CPU compression time can exceed network savings.")
        print("   This will reverse in favor of Gzip once deployed to the cloud!")
    print("="*45)

if __name__ == "__main__":
    benchmark()


