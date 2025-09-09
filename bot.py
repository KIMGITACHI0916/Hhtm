# bot.py
import os
from dotenv import load_dotenv
from telegram.ext import Application, ChatMemberHandler
from scheduler import start_group_scheduler, stop_group_scheduler
from db.models import groups
from telegram import Update
from telegram.ext import ContextTypes

# 🔹 Load env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Bot added/removed from group ---
async def handle_group_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member_update = update.my_chat_member
    chat = chat_member_update.chat
    new_status = chat_member_update.new_chat_member.status
    old_status = chat_member_update.old_chat_member.status

    # ✅ Bot added
    if new_status in ["member", "administrator"] and chat.type in ["group", "supergroup"]:
        groups.update_one(
            {"chat_id": chat.id},
            {"$set": {"chat_id": chat.id, "title": chat.title}},
            upsert=True
        )
        start_group_scheduler(context.application, chat.id)
        print(f"[Bot] Added to {chat.title}")

    # ❌ Bot removed
    elif old_status in ["member", "administrator"] and new_status == "left":
        groups.delete_one({"chat_id": chat.id})
        stop_group_scheduler(chat.id)
        print(f"[Bot] Removed from {chat.title}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(ChatMemberHandler(handle_group_status, chat_member=True))
    app.run_polling()


if __name__ == "__main__":
    main()
    
