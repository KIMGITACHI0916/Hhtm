import os
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = "waifubot"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

users = db["users"]
waifus = db["waifus"]
active_drops = db["active_drops"]

def init_db():
    users.create_index("user_id", unique=True)
    waifus.create_index("name")
    active_drops.create_index("chat_id", unique=True)

# 🔹 Add user (called in /start)
def add_user(user_id: int, username: str):
    users.update_one(
        {"user_id": user_id},
        {
            "$setOnInsert": {
                "user_id": user_id,
                "username": username,
                "harem": []
            },
            "$set": {
                "username": username  # update if changed
            }
        },
        upsert=True
    )

# 🔹 Add waifu to user harem
def add_waifu_to_harem(user_id: int, waifu: dict):
    """
    waifu = {
        "name": "Mikasa Ackerman",
        "series": "Attack On Titan",
        "rarity": "Winter"
        "id": 122,
    }
    """
    # Add new waifu if not already collected
    users.update_one(
        {"user_id": user_id, "harem.id": {"$ne": waifu["id"]}},
        {"$push": {"harem": {**waifu, "count": 1}}},
    )

    # If waifu already exists, increase count
    users.update_one(
        {"user_id": user_id, "harem.id": waifu["id"]},
        {"$inc": {"harem.$.count": 1}},
    )

# 🔹 Get user harem
def get_harem(user_id: int):
    user = users.find_one({"user_id": user_id}, {"harem": 1})
    return user.get("harem", []) if user else []
    
