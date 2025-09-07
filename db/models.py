import os
from pymongo import MongoClient
import certifi

# Use MONGO_URL from environment
MONGO_URL = os.getenv("MONGO_URL") or "mongodb+srv://Slaveyourwaifu:9078522044@cluster0.qemnb4e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "waifubot"

# Connect with TLS/SSL using certifi
client = MongoClient(MONGO_URL, tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=50000)
db = client[DB_NAME]

users = db["users"]
waifus = db["waifus"]
active_drops = db["active_drops"]

def init_db():
    """Create necessary indexes."""
    users.create_index("user_id", unique=True)
    waifus.create_index("name")
    active_drops.create_index("chat_id", unique=True)

# Add user
def add_user(user_id: int, username: str):
    users.update_one(
        {"user_id": user_id},
        {
            "$setOnInsert": {"user_id": user_id, "username": username, "harem": []},
            "$set": {"username": username},
        },
        upsert=True
    )

# Add waifu to user harem
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
        {"$project": {"user_id": "$_id", "username": "$user_info.username", "total": 1}}
    ]
    return list(users.aggregate(pipeline))
    
