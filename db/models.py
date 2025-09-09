import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "waifubot")

# Connect to MongoDB Atlas with proper TLS
client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client[DB_NAME]

# Collections
users = db["users"]
waifus = db["waifus"]
active_drops = db["active_drops"]
groups = db["groups"]  

def init_db():
    """Create indexes if they don't exist"""
    users.create_index("user_id", unique=True)
    waifus.create_index("name")
    active_drops.create_index("chat_id", unique=True)
    groups.create_index("chat_id", unique=True)  # ✅ index for groups
    print("[INFO] Database initialized.")

# Add user safely
def add_user(user_id: int, username: str):
    user = users.find_one({"user_id": user_id})
    if not user:
        users.insert_one({"user_id": user_id, "username": username, "harem": []})
    elif user.get("username") != username:
        users.update_one({"user_id": user_id}, {"$set": {"username": username}})

# Add waifu to harem
def add_waifu_to_harem(user_id: int, waifu: dict):
    users.update_one(
        {"user_id": user_id, "harem.id": {"$ne": waifu["id"]}},
        {"$push": {"harem": {**waifu, "count": 1}}},
    )
    users.update_one(
        {"user_id": user_id, "harem.id": waifu["id"]},
        {"$inc": {"harem.$.count": 1}},
    )

# Get user harem
def get_harem(user_id: int):
    user = users.find_one({"user_id": user_id}, {"harem": 1})
    return user.get("harem", []) if user else []

# Leaderboard
def get_leaderboard(limit: int = 10):
    pipeline = [
        {"$unwind": "$harem"},
        {"$group": {"_id": "$user_id", "total": {"$sum": "$harem.count"}}},
        {"$sort": {"total": -1}},
        {"$limit": limit},
        {"$lookup": {"from": "users", "localField": "_id", "foreignField": "user_id", "as": "user_info"}},
        {"$unwind": "$user_info"},
        {"$project": {"user_id": "$_id", "username": "$user_info.username", "total": 1}},
    ]
    return list(users.aggregate(pipeline))

# ✅ Add group safely
def add_group(chat_id: int, title: str):
    groups.update_one(
        {"chat_id": chat_id},
        {"$set": {"title": title}},
        upsert=True,
    )

# ✅ Get all group IDs for /startdropping
def get_all_group_ids():
    """Return a list of all chat_ids for groups where bot is active."""
    result = groups.find({}, {"chat_id": 1})
    return [g["chat_id"] for g in result]
    
