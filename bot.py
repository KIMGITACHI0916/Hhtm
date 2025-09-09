import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
from db.models import init_db, add_user
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
    chat_id = chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="Welcome to WaifuBot! Waifus will drop randomly. Use /grab to collect them!"
    )

    # Start scheduler for this group
    if chat.type in ["group", "supergroup"]:
        asyncio.create_task(start_scheduler(context.application, chat.id))
        print(f"[INFO] Scheduler started in group {chat.id}")

# --- /drop command for manual testing ---
async def manual_drop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await drop_waifu(context.application, chat_id)
    await context.bot.send_message(chat_id=chat_id, text="Waifu drop triggered manually!")

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
        # Additional command handlers can be added later
        # app.add_handler(CommandHandler("grab", handle_collect))
        # app.add_handler(CommandHandler("harem", handle_harem))
        # app.add_handler(CommandHandler("info", handle_info))
        # app.add_handler(CommandHandler("top", handle_leaderboard))

        print("✅ Handlers attached")
        print("✅ Commands registered")

        # Start scheduler after bot is ready
        async def post_init(application):
            print("⚡ Scheduler starting...")
            asyncio.create_task(start_scheduler(application))

        app.post_init = post_init

        print("📡 Starting polling...")
        app.run_polling()

    except Exception as e:
        import traceback
        print("❌ Fatal error:", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
    
