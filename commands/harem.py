from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
)
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ContextTypes,
)
from db.models import get_user_harem
import math


# Rarity Emojis
RARITY_EMOJIS = {
    "Common": "⚪",
    "Uncommon": "🟢",
    "Rare": "🟣",
    "Legendary": "🟡",
    "Special": "💮",
    "Limited": "🔮",
    "Celestial": "🎐",
    "Valentine": "💖",
    "Winter": "❄️",
    "AMV": "💌",
}


# ---------------- COMMAND ----------------
async def show_harem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show menu with buttons that trigger inline query."""
    user_id = update.effective_user.id

    buttons = [
        [
            InlineKeyboardButton(
                "📸 Collection",
                switch_inline_query_current_chat=f"user_slaves.{user_id}",
            ),
            InlineKeyboardButton(
                "💌 AMV",
                switch_inline_query_current_chat=f"amv.{user_id}",
            ),
        ]
    ]
    kb = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🌸 𝑺𝒍𝒂𝒗𝒆 𝑯𝒂𝒓𝒆𝒎 🌸\nChoose an option:", reply_markup=kb)


# ---------------- INLINE QUERY ----------------
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show harem as gallery when user types inline query."""
    query = update.inline_query.query

    if not query.startswith(("user_slaves.", "amv.")):
        return

    # Extract user id
    try:
        user_id = int(query.split(".")[1])
    except:
        return

    harem = get_user_harem(user_id)
    if not harem:
        await update.inline_query.answer([])
        return

    # Filter AMV if needed
    if query.startswith("amv."):
        harem = [w for w in harem if w.get("rarity") == "AMV"]

    results = []
    for idx, w in enumerate(harem[:50]):  # Telegram inline query has a 50-item limit
        rarity = w.get("rarity", "Unknown")
        emoji = RARITY_EMOJIS.get(rarity, "❔")
        caption = (
            f"✨ {w.get('name','Unknown')}\n"
            f"{emoji} Rarity: {rarity}\n"
            f"📦 Count: {w.get('count',1)}\n"
            f"🎭 Source: {w.get('desc','Unknown')}"
        )

        image_url = (
            w.get("image_url")
            or w.get("image")
            or w.get("url")
            or "https://via.placeholder.com/300x400.png?text=No+Image"
        )

        results.append(
            InlineQueryResultPhoto(
                id=str(idx),
                photo_url=image_url,
                thumb_url=image_url,
                caption=caption,
            )
        )

    await update.inline_query.answer(results, cache_time=1)


# ---------------- HANDLERS ----------------
def get_harem_handlers():
    return [
        CommandHandler(["harem", "collection"], show_harem),
        InlineQueryHandler(inline_query),
    ]
    
