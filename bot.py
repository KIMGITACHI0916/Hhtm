# bot.py
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler
)
from db.models import init_db, groups
from scheduler import drop_waifu, start_scheduler, start_scheduler, stop_scheduler, start_global_scheduler


# --- Load env ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# --- Track group join/leave ---
async def handle_group_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member_update = update.my_chat_member
    if not chat_member_update:
        return

    chat = chat_member_update.chat
    new_status = chat_member_update.new_chat_member.status
    old_status = chat_member_update.old_chat_member.status

    # Bot added to group
    if new_status in ["member", "administrator"] and chat.type in ["group", "supergroup"]:
        groups.update_one(
            {"chat_id": chat.id},
            {"$set": {"chat_id": chat.id, "title": chat.title}},
            upsert=True
        )
        print(f"[INFO] Bot added to group: {chat.title} ({chat.id})")

    # Bot removed from group
    elif old_status in ["member", "administrator"] and new_status == "left":
        groups.delete_one({"chat_id": chat.id})
        print(f"[INFO] Bot removed from group: {chat.title} ({chat.id})")

# --- Example start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive! Use /startdropping to begin drops.")

# --- Manual start dropping ---
async def start_dropping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    asyncio.create_task(start_scheduler(context.application, chat_id))
    await context.bot.send_message(chat_id=chat_id, text="🚀 Drops started in this group!")

# --- Main ---
def main():
    print("🚀 Starting bot...")
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("startdropping", start_dropping))

    # Track group join/leave
    app.add_handler(ChatMemberHandler(handle_group_status, chat_member_types=["my_chat_member"]))

    # Start global scheduler
    start_global_scheduler()

    print("📡 Bot running...")
    app.run_polling()

    
