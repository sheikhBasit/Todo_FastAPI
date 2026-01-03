import requests
import random
import time

BASE_URL = "http://localhost:8000"

# --- EXPANDED TASK POOL ---
# We add many more options so users don't look identical
TASK_POOL = {
    "Work": [
        {"title": "Submit Project Alpha", "description": "Critical deadline approaching."},
        {"title": "Review Bug Reports", "description": "Important for the next release."},
        {"title": "Team Standup", "description": "Routine morning sync."},
        {"title": "Email Client", "description": "Follow up on the invoice."},
        {"title": "Finish Slide Deck", "description": "Urgent: Presentation at 3 PM."}
    ],
    "Learning": [
        {"title": "Finish Docker Course", "description": "Urgent certification goal."},
        {"title": "Read SQLAlchemy Docs", "description": "Learn about advanced joins."},
        {"title": "Practice LeetCode", "description": "Keep algorithms sharp."},
        {"title": "Submit Research Paper", "description": "Final deadline for submission."},
        {"title": "Watch FastAPI Tutorial", "description": "Improve backend skills."}
    ],
    "Fitness": [
        {"title": "Urgent Physio Session", "description": "Recovery for the injury."},
        {"title": "Go for a Run", "description": "Target: 5km in 25 mins."},
        {"title": "Gym - Chest Day", "description": "Focus on bench press."},
        {"title": "Check Weight Progress", "description": "Weekly monitoring."},
        {"title": "Buy Protein Powder", "description": "Supplements are running low."}
    ],
    "Personal": [
        {"title": "Pay Electricity Bill", "description": "Deadline is today!"},
        {"title": "Call Home", "description": "Check in with family."},
        {"title": "Submit Tax Return", "description": "Important financial task."},
        {"title": "Organize Room", "description": "Cleanup session."},
        {"title": "Book Dental Exam", "description": "Routine checkup needed."}
    ],
    "Shopping": [
        {"title": "Buy Urgent Groceries", "description": "Milk and eggs are finished."},
        {"title": "Order New Laptop", "description": "The current one is lagging."},
        {"title": "Check Gift Deals", "description": "Buy something for Sarah's birthday."},
        {"title": "Review Cart", "description": "Amazon checkout list."},
        {"title": "Finish Shopping List", "description": "Write down items for the weekend."}
    ]
}

CATEGORIES = list(TASK_POOL.keys())

def seed():
    print(f"🚀 Starting Randomized API Seeding at {BASE_URL}...")

    for i in range(1, 11):
        username = f"DevUser{i}"
        email = f"user{i}@example.com"
        password = "password123"

        # 1. REGISTER & LOGIN
        reg_payload = {"username": username, "email": email, "password": password}
        requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
        
        login_data = {"username": username, "password": password}
        login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_resp.status_code != 200:
            print(f"❌ Failed to process {username}")
            continue
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. RANDOMIZED SELECTION
        # Pick 2 or 3 random categories for this specific user
        user_categories = random.sample(CATEGORIES, k=random.randint(2, 4))
        
        print(f"👤 {username}: Selected {len(user_categories)} categories...")

        for cat in user_categories:
            # Create Group
            group_resp = requests.post(f"{BASE_URL}/groups/", json={"name": cat}, headers=headers)
            
            if group_resp.status_code == 200:
                group_id = group_resp.json()["id"]
                
                # Pick 2-3 random tasks from the pool for this category
                tasks_to_add = random.sample(TASK_POOL[cat], k=random.randint(1, 3))
                
                for task_info in tasks_to_add:
                    task_payload = {
                        "title": task_info["title"],
                        "description": task_info["description"],
                        "group_id": group_id,
                        "is_completed": False
                    }
                    requests.post(f"{BASE_URL}/tasks/", json=task_payload, headers=headers)
        
        print(f"✅ {username}: Data seeded with unique priority.")

    print("\n🏁 Randomized Seeding Complete!")

if __name__ == "__main__":
    seed()