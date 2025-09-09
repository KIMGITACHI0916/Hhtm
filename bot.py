
# bot.py
import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from db.models import init_db, active_drops, add_waifu_to_harem
from scheduler import drop_waifu, start_scheduler

# Load .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Waifu bot is online.")

async def grab(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /grab <waifu_name>")
        return

    waifu_name = " ".join(args)
    drop = active_drops.find_one({"chat_id": update.effective_chat.id})
    if not drop:
        await update.message.reply_text("No waifu to grab right now.")
        return

    waifu = drop["waifu"]
    if waifu_name.lower() != waifu["name"].lower():
        await update.message.reply_text(f"{waifu_name} is not available!")
        return

    # Add to user harem
    add_waifu_to_harem(user_id, waifu)
    await update.message.reply_text(f"🎉 You grabbed {waifu['name']}!")

    # Remove from active drops
    active_drops.delete_one({"chat_id": update.effective_chat.id})

async def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    # Add bot command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grab", grab))

    # Start the scheduler as a background task inside the bot
    app.create_task(start_scheduler(app))

    print("[INFO] Bot is running…")
    await app.run_polling()

# Entry point
if __name__ == "__main__":
    # Directly run main without wrapping in asyncio.run() if running in interactive/looped env
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Fallback if event loop is already running (like in Jupyter or certain Docker setups)
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        
