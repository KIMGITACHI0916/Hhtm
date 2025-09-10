import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from db.models import init_db, add_waifu_to_harem, active_drops
from scheduler import start_scheduler
from group_manager import register_group
from commands.upload import get_upload_handler
from commands.groups import get_groups_handler

load_dotenv()
TOKEN = os.getenv("TOKEN")

# --- Memory for collected per chat ---
collected = {}

# --- Grab/Collect Logic ---
async def grab_waifu(chat_id, user, guess_name=None):
    drop = active_drops.find_one({"chat_id": chat_id})
    if not drop or "waifu" not in drop:
        return None  # no active waifu drop

    waifu = drop["waifu"]
    waifu_id = waifu["id"]

    if chat_id not in collected:
        collected[chat_id] = set()

    if waifu_id in collected[chat_id]:
        return "already"

    if guess_name:
        guess_name = guess_name.lower().strip()
        waifu_full = waifu["name"].lower()
        waifu_parts = waifu_full.split()

        # accept full name, first name, or last name
        if guess_name != waifu_full and guess_name not in waifu_parts:
            return "wrong"

    # mark as collected
    collected[chat_id].add(waifu_id)
    add_waifu_to_harem(user.id, waifu)
    active_drops.delete_one({"chat_id": chat_id})  # remove active drop

    return waifu

# --- Send Result Message ---
async def send_grab_result(update, result):
    if result == "already":
        await update.message.reply_text("⚠️ This waifu has already been grabbed!")
    elif result == "wrong":
        return  # ignore silently
    elif result:
        waifu = result
        username = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else update.effective_user.full_name
        )
        msg = (
            "🌸 𝑺𝒍𝒂𝒗𝒆 𝑪𝒐𝒍𝒍𝒆𝒄𝒕𝒊𝒐𝒏 𝑼𝒑𝒅𝒂𝒕𝒆 🌸\n\n"
            f"💖 Character: {waifu['name']}\n"
            f"🎬 From: {waifu.get('desc', 'Unknown')}\n"
            f"💎 Rarity: {waifu.get('rarity', 'Unknown')}\n"
            f"🆔 Id: {waifu['id']}\n\n"
            f"📖 Grabbed by ➝ {username}"
        )
        await update.message.reply_text(msg)

# --- /grab and /collect command ---
async def handle_grab_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: /grab <waifu name> or /collect <waifu name>")
        return

    guess_name = " ".join(context.args)
    result = await grab_waifu(update.effective_chat.id, update.effective_user, guess_name)
    await send_grab_result(update, result)

# --- Plain text name detection ---
async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text or not update.effective_chat:
        return

    result = await grab_waifu(update.effective_chat.id, update.effective_user, text)
    await send_grab_result(update, result)

# --- /start ---
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Waifu bot is online.")

# --- Post-init ---
async def on_post_init(application):
    print("[INFO] Starting scheduler…")
    application.create_task(start_scheduler(application))

# --- Main ---
def main():
    init_db()
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(on_post_init)
        .build()
    )

    # --- Handlers ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(get_upload_handler())
    app.add_handler(get_groups_handler())
    app.add_handler(MessageHandler(filters.ALL, register_group))

    # Grab/Collect handlers
    app.add_handler(CommandHandler(["grab", "collect"], handle_grab_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))

    print("[INFO] Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
        
