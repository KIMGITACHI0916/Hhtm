import asyncio
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ChatMemberHandler,
)
from db.models import init_db, add_user
from commands.waifulist import get_waifulist_handler
from commands.collect import handle_collect
from commands.harem import handle_harem
from commands.info import handle_info
from commands.leaderboard import handle_leaderboard
from commands.upload import get_upload_handler
from scheduler import start_scheduler, drop_waifu, add_handlers
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# --- /start command handler ---
async def start(update, context):
    user = update.effective_user
    chat = update.effective_chat

    add_user(user.id, user.username)
    await update.message.reply_text(
        "Welcome to WaifuBot! Waifus will drop randomly. Use /grab to collect them!"
    )

    # Start scheduler for this group if added manually via /start
    if chat.type in ["group", "supergroup"]:
        asyncio.create_task(start_scheduler(context.application, chat.id))
        print(f"[INFO] Scheduler manually started in group {chat.id}")

# --- Optional: manual /drop command for testing ---
async def manual_drop(update, context):
    await drop_waifu(context.application.bot, update.effective_chat.id)

# --- Main function ---
def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    # Attach auto group tracking
    add_handlers(app)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grab", handle_collect))
    app.add_handler(CommandHandler("harem", handle_harem))
    app.add_handler(CommandHandler("info", handle_info))
    app.add_handler(CommandHandler("top", handle_leaderboard))
    app.add_handler(CommandHandler("drop", manual_drop))
    app.add_handler(get_waifulist_handler())
    app.add_handler(get_upload_handler())

    print("✅ Bot is running...")

    # 🔥 Run global scheduler
    asyncio.create_task(start_scheduler(app))

    app.run_polling()
    
