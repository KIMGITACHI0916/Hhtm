from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from db.models import get_user_harem
from collections import defaultdict
import math

ITEMS_PER_PAGE = 5  # anime groups per page
PHOTOS_PER_PAGE = 10  # how many images per gallery page

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

# --- Text mode (list style)
def format_harem(harem, page: int = 1):
    grouped = defaultdict(list)
    for waifu in harem:
        grouped[waifu.get("desc", "Unknown")].append(waifu)

    sources = list(grouped.keys())
    total_pages = max(1, math.ceil(len(sources) / ITEMS_PER_PAGE))
    page = max(1, min(page, total_pages))

    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    selected_sources = sources[start:end]

    text = f"🌸 𝑺𝒍𝒂𝒗𝒆 𝑯𝒂𝒓𝒆𝒎 🌸\n\n"

    for src in selected_sources:
        chars = grouped[src]
        text += f"⇒ {src} {len(chars)}\n"
        text += "-------------------\n"
        for w in chars:
            rarity = w.get("rarity", "Unknown")
            emoji = RARITY_EMOJIS.get(rarity, "❔")
            text += f"↳ {w['id']} | {emoji} {w['name']} x{w.get('count', 1)}\n"
        text += "-------------------\n"

    buttons = [
        [
            InlineKeyboardButton("⬅", callback_data=f"harem:{page-1}"),
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"),
            InlineKeyboardButton("➡", callback_data=f"harem:{page+1}")
        ],
        [
            InlineKeyboardButton("🖼 Collection", callback_data="collection:1"),
            InlineKeyboardButton("💌 AMV", callback_data="amv:1")
        ]
    ]
    return text, InlineKeyboardMarkup(buttons)

# --- Show text harem
async def show_harem(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1):
    user_id = update.effective_user.id
    harem = get_user_harem(user_id)

    if not harem:
        await update.message.reply_text("📭 Your harem is empty!")
        return

    text, kb = format_harem(harem, page)
    await update.message.reply_text(text, reply_markup=kb)

# --- Gallery mode
async def show_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1, filter_rarity=None):
    query = update.callback_query
    user_id = query.from_user.id
    harem = get_user_harem(user_id)

    if filter_rarity:
        harem = [w for w in harem if w.get("rarity") == filter_rarity]

    if not harem:
        await query.answer("📭 No items found!", show_alert=True)
        return

    total_pages = max(1, math.ceil(len(harem) / PHOTOS_PER_PAGE))
    page = max(1, min(page, total_pages))

    start = (page - 1) * PHOTOS_PER_PAGE
    end = start + PHOTOS_PER_PAGE
    selected = harem[start:end]

    media = []
    for w in selected:
        if w.get("image_url"):
            caption = f"{w['name']} | {w.get('rarity','❔')}"
            media.append(InputMediaPhoto(media=w['image_url'], caption=caption))

    if media:
        await query.message.delete()
        await query.message.reply_media_group(media)

    buttons = [
        [
            InlineKeyboardButton("⬅", callback_data=f"{filter_rarity.lower()}:{page-1}"),
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"),
            InlineKeyboardButton("➡", callback_data=f"{filter_rarity.lower()}:{page+1}")
        ],
        [InlineKeyboardButton("📜 Back to list", callback_data="harem:1")]
    ]
    await query.message.reply_text("🖼 Gallery View", reply_markup=InlineKeyboardMarkup(buttons))

# --- Button handler
async def harem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")

    if data[0] == "harem":
        page = int(data[1]) if data[1].isdigit() else 1
        user_id = query.from_user.id
        harem = get_user_harem(user_id)
        text, kb = format_harem(harem, page)
        await query.edit_message_text(text, reply_markup=kb)

    elif data[0] in ["collection", "amv"]:
        page = int(data[1]) if data[1].isdigit() else 1
        filter_rarity = "AMV" if data[0] == "amv" else None
        await show_gallery(update, context, page, filter_rarity)

def get_harem_handlers():
    return [
        CommandHandler(["harem", "collection"], show_harem),
        CallbackQueryHandler(harem_callback, pattern="^(harem|collection|amv):")
    ]
    
