import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from db.models import init_db, add_user
from commands.waifulist import get_waifulist_handler
from commands.collect import handle_collect
from commands.harem import handle_harem
from commands.info import handle_info
from commands.leaderboard import handle_leaderboard
from commands.upload import get_upload_handler   # ✅ ADD THIS
from scheduler import start_scheduler, drop_waifu
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = None

async def start(update, context):
    global GROUP_CHAT_ID
    user = update.effective_user
    chat = update.effective_chat

    add_user(user.id, user.username)
    await update.message.reply_text(
        "Welcome to WaifuBot! Waifus will drop randomly. Use /collect to grab them!"
    )

    if chat.type in ["group", "supergroup"]:
        GROUP_CHAT_ID = chat.id
        print(f"[INFO] Scheduler activated in group {GROUP_CHAT_ID}")
        asyncio.create_task(start_scheduler(context.application, GROUP_CHAT_ID))

def main():
    init_db()  # Initialize MongoDB collections & indexes
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grab", handle_collect))
    app.add_handler(CommandHandler("harem", handle_harem))
    app.add_handler(CommandHandler("info", handle_info))
    app.add_handler(CommandHandler("top", handle_leaderboard))
    app.add_handler(CommandHandler("drop", lambda update, context: asyncio.create_task(drop_waifu(app.bot, update.effective_chat.id))))
    app.add_handler(get_waifulist_handler())
    app.add_handler(get_upload_handler())

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
