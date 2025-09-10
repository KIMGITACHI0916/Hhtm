from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from db.models import add_waifu_to_harem, active_drops

# Track grabbed waifus per chat to prevent duplicates
collected = {}

# Rarity → Emoji mapping
RARITY_EMOJIS = {
    "Common": "⚪",
    "Uncommon": "🟢",
    "Rare": "🟣",
    "Legendary": "🟡",
    "Special": "💮",
    "Celestial": "🎐"
}

# --- Grab logic ---
async def grab_waifu(chat_id, user, guess_name=None):
    """Handles the actual grab/collect logic for a chat and user."""
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

    # --- Matching logic ---
    if guess_name:
        guess_name = guess_name.lower().strip()
        waifu_full = waifu["name"].lower()
        waifu_parts = waifu_full.split()

        # Accept full name, first name, or last name
        if (
            guess_name != waifu_full
            and guess_name not in waifu_parts
        ):
            return "wrong"

    # Mark as collected
    collected[chat_id].add(waifu_id)

    # Add to user's harem
    add_waifu_to_harem(user.id, waifu)

    # Remove active drop from DB
    active_drops.delete_one({"chat_id": chat_id})

    return waifu

# --- Shared result message ---
async def send_grab_result(update, result):
    if result == "already":
        await update.message.reply_text("⚠️ This waifu has already been grabbed!")
    elif result == "wrong":
        return  # silently ignore wrong guesses
    elif result:
        waifu = result
        username = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else update.effective_user.full_name
        )

        rarity = waifu.get("rarity", "Unknown")
        rarity_emoji = RARITY_EMOJIS.get(rarity, "")

        msg = (
            "🌸 𝑺𝒍𝒂𝒗𝒆 𝑪𝒐𝒍𝒍𝒆𝒄𝒕𝒊𝒐𝒏 𝑼𝒑𝒅𝒂𝒕𝒆 🌸\n\n"
            f"💖 Character: {waifu['name']}\n"
            f"🎬 From: {waifu.get('desc', 'Unknown').replace('From ', '')}\n"
            f"💎 Rarity: {rarity} {rarity_emoji}\n"
            f"🆔 Id: {waifu['id']}\n\n"
            f"📖 Grabbed by ➝ {username}"
        )
        await update.message.reply_text(msg)

# --- /grab and /collect command handler ---
async def handle_grab_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: /grab <waifu name> or /collect <waifu name>")
        return

    guess_name = " ".join(context.args)
    result = await grab_waifu(update.effective_chat.id, update.effective_user, guess_name)
    await send_grab_result(update, result)

# --- Generic message handler for typing waifu name directly ---
async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text or not update.effective_chat:
        return

    result = await grab_waifu(update.effective_chat.id, update.effective_user, text)
    await send_grab_result(update, result)

# --- Function to register handlers in bot.py ---
def get_collect_handlers():
    return [
        CommandHandler(["grab", "collect"], handle_grab_command),  # both commands work
        MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message)  # plain text names
    ]
    
