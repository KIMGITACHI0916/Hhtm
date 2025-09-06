import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, Application
from db.models import init_db, add_user
from commands.collect import handle_collect
from commands.harem import handle_harem
from commands.info import handle_info
from commands.leaderboard import handle_leaderboard
from commands.upload import get_upload_handler   # ✅ NEW
from scheduler import start_scheduler
from scheduler import drop_waifu  # import at top


TOKEN = "8408998512:AAFELhAxHrIH6Llv-lvA1Nrg_mHr-8nXHBM"   # 🚨 Replace with your actual token, don’t share it publicly!

# this will be set dynamically after /start in a group
GROUP_CHAT_ID = None  

async def start(update, context):
    global GROUP_CHAT_ID
    user = update.effective_user
    chat = update.effective_chat

    add_user(user.id, user.username)
    await update.message.reply_text(
        "Welcome to WaifuBot! Waifus will drop randomly. Use /collect to grab them!"
    )

    # ✅ if the bot is started inside a group, save its ID
    if chat.type in ["group", "supergroup"]:
        GROUP_CHAT_ID = chat.id
        print(f"[INFO] Scheduler activated in group {GROUP_CHAT_ID}")
        asyncio.create_task(start_scheduler(context.application, GROUP_CHAT_ID))

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("collect", handle_collect))
    app.add_handler(CommandHandler("harem", handle_harem))
    app.add_handler(CommandHandler("info", handle_info))
    app.add_handler(CommandHandler("top", handle_leaderboard))
    app.add_handler(CommandHandler("drop", lambda update, context: asyncio.create_task(drop_waifu(app.bot, update.effective_chat.id))))
    app.add_handler(get_upload_handler())   # ✅ Register /upload

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
