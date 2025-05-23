import json
import os

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
HABITS_FILE = os.path.join(DATA_DIR, "habits.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")

def init_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for file in [USERS_FILE, HABITS_FILE, LOGS_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump([], f)

init_files()

def read_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_habits():
    with open(HABITS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_habits(data):
    with open(HABITS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_logs():
    with open(LOGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_logs(data):
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
