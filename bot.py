import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db.models import init_db, add_waifu_to_harem, active_drops
from scheduler import start_scheduler

load_dotenv()
TOKEN = os.getenv("TOKEN")

# --- Handlers ---
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

    add_waifu_to_harem(user_id, waifu)
    await update.message.reply_text(f"🎉 You grabbed {waifu['name']}!")
    active_drops.delete_one({"chat_id": update.effective_chat.id})

# --- Main ---
def main():
    init_db()
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("grab", grab))

    async def startup_task():
        print("[INFO] Starting scheduler…")
        await start_scheduler(application)

    # Schedule the startup_task **after the bot initializes**
    application.create_task(startup_task())

    print("[INFO] Bot is running…")
    application.run_polling()  # PTB manages the event loop

if __name__ == "__main__":
    main()
