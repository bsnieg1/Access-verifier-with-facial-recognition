import json
from pathlib import Path

USERS_FILE = Path("data/users.json")


def load_users():
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def add_user(name: str):
    users = load_users()

    # nowe ID (max + 1)
    new_id = str(max(map(int, users.keys()), default=0) + 1)

    users[new_id] = {
        "name": name
    }

    save_users(users)
    return new_id


def get_user(user_id: str):
    users = load_users()
    return users.get(user_id)
