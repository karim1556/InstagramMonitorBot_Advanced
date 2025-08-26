import json
import os

DB_FILE = "user_data.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_user(user_id, username):
    data = load_users()
    if str(user_id) not in data:
        data[str(user_id)] = {"targets": []}
    if username not in data[str(user_id)]["targets"]:
        data[str(user_id)]["targets"].append(username)
    save_users(data)

def get_all_targets():
    data = load_users()
    targets = {}
    for uid, info in data.items():
        for username in info["targets"]:
            targets[username] = int(uid)
    return targets