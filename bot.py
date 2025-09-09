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
from db.models import init_db, add_user, add_group, get_all_group_ids
from scheduler import start_scheduler, drop_waifu, add_handlers

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# --- /start command handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # Add user to database
    add_user(user.id, user.username)

    # Safe welcome message
    await context.bot.send_message(
        chat_id=chat.id,
        text="Welcome to WaifuBot! Waifus will drop randomly. Use /grab to collect them!"
    )

# --- /drop command for manual testing ---
async def manual_drop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await drop_waifu(context.application, chat_id)
    await context.bot.send_message(chat_id=chat_id, text="Waifu drop triggered manually!")

# --- /startdropping command to start scheduler in all groups ---
async def start_dropping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Fetch all group IDs from database
    group_ids = get_all_group_ids()

    if not group_ids:
        await context.bot.send_message(chat_id=chat_id, text="No groups found to start dropping.")
        return

    # Start scheduler in all groups
    for gid in group_ids:
        asyncio.create_task(start_scheduler(context.application, gid))
        print(f"[INFO] Scheduler started in group {gid}")

    await context.bot.send_message(chat_id=chat_id, text="✅ Waifu dropping started in all groups!")

# --- Auto-track groups when bot is added ---
async def track_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    new_status = update.my_chat_member.new_chat_member.status

    # If bot was added to a group
    if new_status in ["member", "administrator"] and chat.type in ["group", "supergroup"]:
        add_group(chat.id, chat.title)
        print(f"[INFO] Bot added to group {chat.title} ({chat.id})")

# --- Main function ---
def main():
    try:
        print("🚀 Bot is starting...")
        init_db()  # Initialize database

        # Build bot application
        app = ApplicationBuilder().token(TOKEN).build()

        # Attach auto group tracking handlers
        add_handlers(app)

        # Register commands
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("drop", manual_drop))
        app.add_handler(CommandHandler("startdropping", start_dropping))

        # Attach ChatMember handler to automatically track groups
        app.add_handler(ChatMemberHandler(track_groups, chat_member_types=["my_chat_member"]))

        print("✅ Handlers attached")
        print("✅ Commands registered")

        # Do NOT auto-start scheduler here
        # post_init removed for manual control

        print("📡 Starting polling...")
        app.run_polling()

    except Exception as e:
        import traceback
        print("❌ Fatal error:", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
        
