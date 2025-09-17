from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from db.models import get_user_harem
from collections import defaultdict
import math

ITEMS_PER_PAGE = 5       # For list view
GALLERY_PAGE_SIZE = 20   # Images per gallery page

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

# ---------------- TEXT MODE ----------------
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
            InlineKeyboardButton("⬅", callback_data=f"harem:{page-1}"),
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"),
            InlineKeyboardButton("➡", callback_data=f"harem:{page+1}")
        ],
        [
            InlineKeyboardButton("📸 Collection", callback_data="collection:1"),
            InlineKeyboardButton("💌 AMV", callback_data="amv:1")
        ]
    ]
    return text, InlineKeyboardMarkup(buttons)

# ---------------- GALLERY MODE ----------------
async def show_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int, filter_rarity=None):
    query = update.callback_query
    user_id = query.from_user.id
    harem = get_user_harem(user_id)

    if not harem:
        await query.edit_message_text("📭 Your harem is empty!")
        return

    # Filter items
    if filter_rarity == "AMV":
        filtered = [w for w in harem if w.get("rarity") == "AMV"]
    else:
        filtered = harem

    total_pages = max(1, math.ceil(len(filtered) / GALLERY_PAGE_SIZE))
    page = max(1, min(page, total_pages))

    start = (page - 1) * GALLERY_PAGE_SIZE
    end = start + GALLERY_PAGE_SIZE
    selected = filtered[start:end]

    if not selected:
        await query.edit_message_text("⚠ No images found.")
        return

    # Show only the first image + caption
    first = selected[0]
    caption = f"{first.get('name','Unknown')} | {first.get('rarity','❔')}"
    media = InputMediaPhoto(media=first["image_url"], caption=caption)

    prefix = "amv" if filter_rarity == "AMV" else "collection"

    buttons = [
        [
            InlineKeyboardButton("⬅", callback_data=f"{prefix}:{page-1}"),
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"),
            InlineKeyboardButton("➡", callback_data=f"{prefix}:{page+1}")
        ],
        [InlineKeyboardButton("📜 Back to list", callback_data="harem:1")]
    ]

    try:
        await query.edit_message_media(
            media=media,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        # Fallback: send as new message (in case same media re-edit fails)
        await query.message.reply_photo(photo=first["image_url"], caption=caption, reply_markup=InlineKeyboardMarkup(buttons))

# ---------------- HANDLERS ----------------
async def show_harem(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1):
    user_id = update.effective_user.id
    harem = get_user_harem(user_id)

    if not harem:
        await update.message.reply_text("📭 Your harem is empty!")
        return

    text, kb = format_harem(harem, page)
    await update.message.reply_text(text, reply_markup=kb)

async def harem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")

    if data[0] == "harem":
        try:
            page = int(data[1])
        except:
            page = 1
        user_id = query.from_user.id
        harem = get_user_harem(user_id)
        text, kb = format_harem(harem, page)
        await query.edit_message_text(text, reply_markup=kb)

    elif data[0] == "collection":
        page = int(data[1]) if len(data) > 1 else 1
        await show_gallery(update, context, page, filter_rarity=None)

    elif data[0] == "amv":
        page = int(data[1]) if len(data) > 1 else 1
        await show_gallery(update, context, page, filter_rarity="AMV")

# Register handlers
def get_harem_handlers():
    return [
        CommandHandler(["harem", "collection"], show_harem),
        CallbackQueryHandler(harem_callback, pattern="^(harem|collection|amv):")
    ]
    
