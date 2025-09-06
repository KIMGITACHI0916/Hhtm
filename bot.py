from telegram.ext import ApplicationBuilder, CommandHandler
from db.models import init_db, add_user
from commands.collect import handle_collect
from commands.harem import handle_harem
from commands.info import handle_info
from commands.leaderboard import handle_leaderboard
from scheduler import start_scheduler

TOKEN = "8408998512:AAGcbJjy_S_lmkXNDClnt6fAmPv2yiXaGI8"
GROUP_CHAT_ID = -4968919749  # Replace with your group chat ID

async def start(update, context):
    user = update.effective_user
    add_user(user.id, user.username)
    await update.message.reply_text("Welcome to WaifuBot! Waifus will drop randomly. Use /collect to grab them!")

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("collect", handle_collect))
    app.add_handler(CommandHandler("harem", handle_harem))
    app.add_handler(CommandHandler("info", handle_info))
    app.add_handler(CommandHandler("top", handle_leaderboard))

    start_scheduler(app.bot, GROUP_CHAT_ID)

    app.run_polling()

if __name__ == "__main__":
    main()
