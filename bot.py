# bot.py
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler
from db.models import init_db
from scheduler import drop_waifu, start_scheduler, handle_group_status

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await context.bot.send_message(chat_id=chat.id, text="Welcome! Waifus will drop randomly!")

async def drop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await drop_waifu(context.application.bot, chat_id)

async def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("drop", drop_command))
    app.add_handler(ChatMemberHandler(handle_group_status, chat_member_types=["my_chat_member"]))

    # start global scheduler
    asyncio.create_task(start_scheduler(app))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
    
