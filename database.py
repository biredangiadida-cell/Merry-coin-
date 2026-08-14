import json
import os

DATA_FILE = "users.json"


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)


def create_user(user_id, first_name, username=None):
    users = load_users()
    uid = str(user_id)

    if uid not in users:
        users[uid] = {
            "id": user_id,
            "first_name": first_name,
            "username": username,
            "coins": 0,
            "referrals": 0,
            "last_daily": ""
        }

        save_users(users)

    return users[uid]


def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))


def update_user(user_id, data):
    users = load_users()
    uid = str(user_id)

    if uid in users:
        users[uid].update(data)
        save_users(users)


def add_coins(user_id, amount):
    users = load_users()
    uid = str(user_id)

    if uid in users:
        users[uid]["coins"] += amount
        save_users(users)

        return users[uid]["coins"]

    return 0
