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

# ----------------- USERS -----------------

def add_user(user_id: int, username: str):
    """Add user safely, update username if changed."""
    user = users.find_one({"user_id": user_id})
    if not user:
        users.insert_one({
            "user_id": user_id,
            "username": username,
            "harem": [],
            "favorite": None  # ✅ default fav
        })
    elif user.get("username") != username:
        users.update_one({"user_id": user_id}, {"$set": {"username": username}})

# ----------------- HAREM -----------------

def add_waifu_to_harem(user_id: int, waifu: dict):
    """Add or increment waifu in harem."""
    users.update_one(
        {"user_id": user_id, "harem.id": {"$ne": waifu["id"]}},
        {"$push": {"harem": {**waifu, "count": 1}}},
    )
    users.update_one(
        {"user_id": user_id, "harem.id": waifu["id"]},
        {"$inc": {"harem.$.count": 1}},
    )

def get_harem(user_id: int):
    """Get user's harem, with fav on top if exists."""
    user = users.find_one({"user_id": user_id}, {"harem": 1, "favorite": 1})
    if not user:
        return []

    harem = user.get("harem", [])
    fav_id = user.get("favorite")

    if fav_id:
        # bring favorite waifu to front
        harem.sort(key=lambda w: 0 if w["id"] == fav_id else 1)

    return harem


# Alias for backwards compatibility
get_user_harem = get_harem


# ----------------- FAVORITE -----------------

def set_favorite(user_id: int, waifu_id: int) -> bool:
    """
    Mark a waifu from harem as favorite.
    Returns True if success, False if waifu not in harem.
    """
    user = users.find_one({"user_id": user_id, "harem.id": waifu_id})
    if not user:
        return False

    users.update_one(
        {"user_id": user_id},
        {"$set": {"favorite": waifu_id}}
    )
    return True

def get_favorite(user_id: int):
    """Return the favorite waifu dict if exists, else None."""
    user = users.find_one({"user_id": user_id}, {"harem": 1, "favorite": 1})
    if not user or not user.get("favorite"):
        return None

    fav_id = user["favorite"]
    for w in user.get("harem", []):
        if w["id"] == fav_id:
            return w
    return None

# ----------------- LEADERBOARD -----------------

def get_leaderboard(limit: int = 10):
    """Leaderboard by total harem count."""
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

# ----------------- GROUPS -----------------

def add_group(chat_id: int, title: str):
    """Register group."""
    groups.update_one(
        {"chat_id": chat_id},
        {"$set": {"title": title}},
        upsert=True,
    )

def get_all_group_ids():
    """Return a list of all chat_ids for groups where bot is active."""
    result = groups.find({}, {"chat_id": 1})
    return [g["chat_id"] for g in result]
    
