from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from db.models import get_user_harem
from collections import defaultdict
import math

ITEMS_PER_PAGE = 5  # anime groups per page

# Map rarity to emoji
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


def format_harem(harem, page: int = 1, mode: str = "harem"):
    grouped = defaultdict(list)

    # Filter based on mode
    for waifu in harem:
        rarity = waifu.get("rarity", "")
        if mode == "amv" and rarity != "AMV":
            continue
        if mode == "collection" and rarity == "AMV":
            continue
        grouped[waifu.get("desc", "Unknown")].append(waifu)

    sources = list(grouped.keys())
    total_pages = max(1, math.ceil(len(sources) / ITEMS_PER_PAGE))
    page = max(1, min(page, total_pages))

    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    selected_sources = sources[start:end]

    header = {
        "harem": "🌸 𝑺𝒍𝒂𝒗𝒆 𝑯𝒂𝒓𝒆𝒎 🌸",
        "collection": "📚 𝑺𝒍𝒂𝒗𝒆 𝑪𝒐𝒍𝒍𝒆𝒄𝒕𝒊𝒐𝒏 📚",
        "amv": "🎬 𝑺𝒍𝒂𝒗𝒆 𝑨𝑴𝑽 🎬"
    }

    text = f"{header.get(mode, '🌸 𝑺𝒍𝒂𝒗𝒆 𝑯𝒂𝒓𝒆𝒎 🌸')}\n\n"

    for src in selected_sources:
        chars = grouped[src]
        text += f"⇒ {src} {len(chars)}/{len(chars)}\n"
        text += "-------------------\n"
        for w in chars:
            rarity = w.get("rarity", "Unknown")
            emoji = RARITY_EMOJIS.get(rarity, "❔")
            text += f"↳ {w['id']} | {emoji} {w['name']} x{w.get('count', 1)}\n"
        text += "-------------------\n"

    # Inline buttons
    buttons = [
        [
            InlineKeyboardButton("⬅", callback_data=f"{mode}:{page-1}"),
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"),
            InlineKeyboardButton("➡", callback_data=f"{mode}:{page+1}")
        ],
        [
            InlineKeyboardButton("📚 Collection", callback_data="collection:1"),
            InlineKeyboardButton("🎬 AMV", callback_data="amv:1"),
        ]
    ]
    return text, InlineKeyboardMarkup(buttons)


# --- Generic show function
async def show_generic(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1, mode: str = "harem"):
    user_id = update.effective_user.id
    harem = get_user_harem(user_id)

    if not harem:
        await update.message.reply_text("📭 Your harem is empty!")
        return

    text, kb = format_harem(harem, page, mode)
    await update.message.reply_text(text, reply_markup=kb)


# --- Button navigation
async def harem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")
    mode = data[0]
    try:
        page = int(data[1])
    except:
        page = 1

    user_id = query.from_user.id
    harem = get_user_harem(user_id)
    text, kb = format_harem(harem, page, mode)
    await query.edit_message_text(text, reply_markup=kb)


def get_harem_handlers():
    return [
        CommandHandler("harem", lambda u, c: show_generic(u, c, mode="harem")),
        CommandHandler("collection", lambda u, c: show_generic(u, c, mode="collection")),
        CommandHandler("amv", lambda u, c: show_generic(u, c, mode="amv")),
        CallbackQueryHandler(harem_callback, pattern="^(harem|collection|amv):")
    ]
    
