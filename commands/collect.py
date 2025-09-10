# commands/collect.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from db.models import add_waifu_to_harem, active_drops

# Track grabbed waifus per chat to prevent duplicates
collected = {}

# --- Grab logic ---
async def grab_waifu(chat_id, user, guess_name=None):
    """Handles the actual grab logic for a chat and user."""
    drop = active_drops.find_one({"chat_id": chat_id})
    if not drop or "waifu" not in drop:
        return None  # no active waifu

    waifu = drop["waifu"]
    waifu_id = waifu["id"]

    # Initialize collected set for this chat
    if chat_id not in collected:
        collected[chat_id] = set()

    # Already grabbed in this chat?
    if waifu_id in collected[chat_id]:
        return "already"

    # Check name if provided
    if guess_name:
        guess_name = guess_name.lower().strip()
        waifu_name_parts = waifu["name"].lower().split()
        if guess_name not in waifu_name_parts and guess_name != waifu["name"].lower():
            return "wrong"

    # Mark as collected
    collected[chat_id].add(waifu_id)

    # Add to user's harem
    add_waifu_to_harem(user.id, waifu)

    # Remove active drop
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

# --- Generic message handler for typing waifu name ---
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

# --- Function to register handlers in bot.py ---
def get_collect_handlers():
    return [
        CommandHandler("grab", handle_grab_command),
        MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message)
    ]
    
