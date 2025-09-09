import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)
from db.models import init_db, add_user
from commands.waifulist import get_waifulist_handler
from commands.collect import handle_collect
from commands.harem import handle_harem
from commands.info import handle_info
from commands.leaderboard import handle_leaderboard
from commands.upload import get_upload_handler
from scheduler import start_scheduler, drop_waifu, add_handlers

# Load env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# --- /start command ---
async def start(update, context):
    user = update.effective_user
    chat = update.effective_chat

    add_user(user.id, user.username)
    await update.message.reply_text(
        "✅ Welcome to WaifuBot!\n"
        "Waifus will drop randomly every 10 minutes.\n"
        "Use /grab to collect them!"
    )

    print(f"[START] {user.username} used /start in chat {chat.id}", flush=True)

# --- Manual drop ---
async def manual_drop(update, context):
    await drop_waifu(context.application.bot, update.effective_chat.id)

def main():
    print("🚀 Bot is starting...", flush=True)

    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN not set in Railway variables!", flush=True)
        return

    init_db()
    print("✅ Database initialized", flush=True)

    app = ApplicationBuilder().token(TOKEN).build()

    # Group tracking
    add_handlers(app)
    print("✅ Handlers attached", flush=True)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grab", handle_collect))
    app.add_handler(CommandHandler("harem", handle_harem))
    app.add_handler(CommandHandler("info", handle_info))
    app.add_handler(CommandHandler("top", handle_leaderboard))
    app.add_handler(CommandHandler("drop", manual_drop))
    app.add_handler(get_waifulist_handler())
    app.add_handler(get_upload_handler())

    print("✅ Commands registered", flush=True)

    async def run():
        print("⚡ Scheduler starting...", flush=True)
        asyncio.create_task(start_scheduler(app))
        print("📡 Starting polling...", flush=True)
        await app.run_polling()

    asyncio.run(run())

if __name__ == "__main__":
    main()
    
