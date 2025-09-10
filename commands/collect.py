    # commands/collect.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from db.models import add_waifu_to_harem, active_drops
from scheduler import current_drop  # dict: chat_id -> active waifu

# Track grabbed waifus per chat to prevent duplicates
collected = {}

# --- Core grab function ---
async def grab_waifu(chat_id, user, guess_name=None):
    if chat_id not in current_drop or not current_drop[chat_id].get("waifu"):
        return None  # no active waifu

    waifu = current_drop[chat_id]["waifu"]
    waifu_id = waifu["id"]

    # Initialize collected set for this chat
    if chat_id not in collected:
        collected[chat_id] = set()

    # Already grabbed
    if waifu_id in collected[chat_id]:
        return "already"

    # Check name if provided
    if guess_name:
        guess_parts = guess_name.lower().split()
        waifu_parts = waifu["name"].lower().split()
        # partial match: any part of guess matches any part of waifu name
        if not any(part in waifu_parts for part in guess_parts):
            return "wrong"

    # Mark as collected
    collected[chat_id].add(waifu_id)

    # Add to DB
    add_waifu_to_harem(user.id, waifu)
    active_drops.delete_one({"chat_id": chat_id})

    return waifu

# --- /grab command handler ---
async def handle_grab_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("ℹ️ Usage: /grab <waifu name>")
        return

    guess_name = " ".join(context.args)
    result = await grab_waifu(update.effective_chat.id, update.effective_user, guess_name)

    if result == "already":
        await update.message.reply_text("⚠️ This waifu has already been grabbed!")
    elif result == "wrong":
        await update.message.reply_text("❌ Wrong name! Try again.")
    elif result:
        # Success message
        waifu = result
        username = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.full_name
        msg = (
            "🌸 𝑺𝒍𝒂𝒗𝒆 𝑪𝒐𝒍𝒍𝒆𝒄𝒕𝒊𝒐𝒏 𝑼𝒑𝒅𝒂𝒕𝒆 🌸\n\n"
            f"💖 Character: {waifu['name']}\n"
            f"🎬 From: {waifu.get('desc', 'Unknown')}\n"
            f"💎 Rarity: {waifu.get('rarity', 'Unknown')}\n"
            f"🆔 Id: {waifu['id']}\n\n"
            f"📖 Grabbed by ➝ {username}"
        )
        await update.message.reply_text(msg)

# --- Handler for normal messages in groups ---
async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text or not update.effective_chat:
        return

    result = await grab_waifu(update.effective_chat.id, update.effective_user, text)
    if result == "already" or result == "wrong" or result is None:
        return  # ignore
    waifu = result
    username = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.full_name
    msg = (
        "🌸 𝑺𝒍𝒂𝒗𝒆 𝑪𝒐𝒍𝒍𝒆𝒄𝒕𝒊𝒐𝒏 𝑼𝒑𝒅𝒂𝒕𝒆 🌸\n\n"
        f"💖 Character: {waifu['name']}\n"
        f"🎬 From: {waifu.get('desc', 'Unknown')}\n"
        f"💎 Rarity: {waifu.get('rarity', 'Unknown')}\n"
        f"🆔 Id: {waifu['id']}\n\n"
        f"📖 Grabbed by ➝ {username}"
    )
    await update.message.reply_text(msg)

# --- Return handlers for bot.py ---
def get_collect_handlers():
    return [
        CommandHandler("grab", handle_grab_command),
        MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message)
    ]
    
