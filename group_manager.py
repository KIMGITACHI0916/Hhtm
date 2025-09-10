# group_manager.py
from telegram import Update
from telegram.ext import ContextTypes
from db.models import groups

async def register_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Register a group automatically when bot sees activity."""
    chat = update.effective_chat
    if chat and chat.type in ["group", "supergroup"]:
        groups.update_one(
            {"chat_id": chat.id},  # filter by group id
            {"$set": {"chat_id": chat.id, "title": chat.title}},
            upsert=True
        )
        print(f"[INFO] Group registered: {chat.title} ({chat.id})")
      
