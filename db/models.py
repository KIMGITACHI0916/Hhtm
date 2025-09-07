import os
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL")  # ✅ get from Railway variable
DB_NAME = "Teasingslave"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

users = db["users"]
waifus = db["waifus"]
active_drops = db["active_drops"]

def init_db():
    users.create_index("user_id", unique=True)
    waifus.create_index("name")
    active_drops.create_index("chat_id", unique=True)
