# bot.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from db.models import init_db
from scheduler import start_scheduler
from group_manager import register_group
from commands.upload import get_upload_handler
from commands.groups import get_groups_handler
from commands.collect import handle_grab_command, handle_group_message  # direct import
from commands.economy import get_economy_handlers  # ✅ new import
from commands.harem import get_harem_handlers  # ✅ new import


load_dotenv()
TOKEN = os.getenv("TOKEN")

# --- Handlers ---
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Waifu bot is online.")

# --- Post-init (scheduler runs in background) ---
async def on_post_init(application):
    print("[INFO] Starting scheduler…")
    application.create_task(start_scheduler(application))  # background, non-blocking

# --- Main ---
def main():
    init_db()
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(on_post_init)  # scheduler starts after bot init
        .build()
    )

    # --- Bot Handlers ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(get_upload_handler())
    app.add_handler(get_groups_handler())

    # ✅ Economy handlers
    for h in get_economy_handlers():
        app.add_handler(h)

    # ✅ Grab/Collect handlers
    app.add_handler(CommandHandler(["grab", "collect"], handle_grab_command))
    app.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP), handle_group_message))


    # --- Harem/Collection handlers ---
    for handler in get_harem_handlers():
        app.add_handler(handler)
        

    
    # ✅ Register group handler last (so it doesn’t block others)
    app.add_handler(MessageHandler(filters.ALL, register_group))

    print("[INFO] Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
    
