# bot.py
import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from db.models import init_db, active_drops, add_waifu_to_harem
from scheduler import start_scheduler

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

    add_waifu_to_harem(user_id, waifu)
    await update.message.reply_text(f"🎉 You grabbed {waifu['name']}!")
    active_drops.delete_one({"chat_id": update.effective_chat.id})

# Post-init function to start the scheduler
async def on_startup(app):
    app.create_task(start_scheduler(app))

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grab", grab))

    # Use PTB post-init hook
    app.post_init(on_startup)

    print("[INFO] Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
    
