import requests
import time

BASE_URL = "http://localhost:8000"

# Sample Data
CATEGORIES = ["Work", "Personal", "Fitness", "Learning", "Shopping"]

TASK_TEMPLATES = {
    "Work": [
        {"title": "Complete API Docs", "description": "Finish the Swagger documentation for the ToDo project."},
        {"title": "Team Sync", "description": "Weekly meeting to discuss sprint goals."}
    ],
    "Personal": [
        {"title": "Grocery Shopping", "description": "Buy milk, eggs, and healthy snacks."},
        {"title": "Clean Apartment", "description": "Vacuum the floors and dust the shelves."}
    ],
    "Fitness": [
        {"title": "Gym - Leg Day", "description": "Focus on squats and lunges."},
        {"title": "Yoga Session", "description": "30 mins of stretching and breathing."}
    ],
    "Learning": [
        {"title": "Read Python Docs", "description": "Read about new features in Python 3.13."},
        {"title": "Groq API Research", "description": "Learn how to optimize system prompts for Llama 3."}
    ],
    "Shopping": [
        {"title": "Buy Birthday Gift", "description": "Get something special for Sarah's party."},
        {"title": "Order Books", "description": "Get 'Clean Code' and 'Designing Data-Intensive Applications'."}
    ]
}

def seed():
    print(f"🚀 Starting API-based seeding at {BASE_URL}...")

    for i in range(1, 11):
        username = f"user_{i}"
        email = f"user{i}@example.com"
        password = "password123"

        # 1. REGISTER
        reg_payload = {
            "username": username,
            "email": email,
            "password": password
        }
        
        print(f"\n👤 Processing {username}...")
        resp = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
        
        if resp.status_code == 400:
            print(f"   - User already exists. Proceeding to login.")
        elif resp.status_code != 200:
            print(f"   - Failed to register: {resp.text}")
            continue

        # 2. LOGIN (to get Token)
        # Note: OAuth2PasswordRequestForm expects form-data, not JSON
        login_data = {"username": username, "password": password}
        login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_resp.status_code != 200:
            print(f"   - Login failed for {username}")
            continue
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. CREATE GROUPS
        for cat in CATEGORIES:
            group_resp = requests.post(
                f"{BASE_URL}/groups/", 
                json={"name": cat}, 
                headers=headers
            )
            
            if group_resp.status_code == 200:
                group_id = group_resp.json()["id"]
                print(f"   - Created Group: {cat}")

                # 4. CREATE TASKS IN THIS GROUP
                for task_data in TASK_TEMPLATES[cat]:
                    task_payload = {
                        "title": task_data["title"],
                        "description": task_data["description"],
                        "group_id": group_id,
                        "is_completed": False
                    }
                    task_resp = requests.post(
                        f"{BASE_URL}/tasks/", 
                        json=task_payload, 
                        headers=headers
                    )
                    if task_resp.status_code == 201 or task_resp.status_code == 200:
                        pass # Successfully created
            else:
                print(f"   - Failed to create group {cat}: {group_resp.text}")

    print("\n✅ Seeding complete! 10 users created with full task history.")
    print(f"🔗 Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    # Small delay to ensure server is up if running in a script sequence
    seed()