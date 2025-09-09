# bot.py
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db.models import init_db, active_drops, add_waifu_to_harem
from scheduler import start_scheduler, drop_waifu

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# -------------------- Handlers --------------------

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

# -------------------- Startup --------------------

async def on_startup(app):
    """Called after Application initialization, before polling."""
    print("[INFO] Starting scheduler…")
    await start_scheduler(app)

# -------------------- Main --------------------

def main():
    init_db()

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(on_startup)  # Scheduler will start after bot is ready
        .build()
    )

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grab", grab))

    print("[INFO] Bot is running…")
    app.run_polling(close_loop=False)  # Avoid event loop errors

if __name__ == "__main__":
    main()
    
