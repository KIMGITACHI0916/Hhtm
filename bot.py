# bot.py
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    ChatMemberHandler
)
from scheduler import drop_waifu, start_scheduler
from db.models import groups

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Waifu Drop Bot ready! 🎐")

# --- Manual Drop Command (for testing) ---
async def drop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await drop_waifu(context.bot, chat_id)

# --- Handle bot added/removed in groups ---
async def handle_group_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member_update = update.my_chat_member
    chat = chat_member_update.chat
    new_status = chat_member_update.new_chat_member.status
    old_status = chat_member_update.old_chat_member.status

    if new_status in ["member", "administrator"] and chat.type in ["group", "supergroup"]:
        groups.update_one(
            {"chat_id": chat.id},
            {"$set": {"chat_id": chat.id, "title": chat.title}},
            upsert=True
        )
        print(f"[BOT] Added to {chat.title} ({chat.id})")

    elif old_status in ["member", "administrator"] and new_status == "left":
        groups.delete_one({"chat_id": chat.id})
        print(f"[BOT] Removed from {chat.title} ({chat.id})")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("drop", drop))  # test only

    # Group add/remove
    app.add_handler(ChatMemberHandler(handle_group_status, ChatMemberHandler.MY_CHAT_MEMBER))

    # Start scheduler loop
    from scheduler import start_scheduler
    asyncio.create_task(start_scheduler(app))

    print("[BOT] Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
