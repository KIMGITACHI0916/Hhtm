from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
    Update,
)
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
)
import re

# Fake DB (replace with real DB)
USER_HAREMS = {
    123456789: [  # Example user_id
        {"name": "Tengen Uzui", "rarity": "Legendary", "image": "https://i.imgur.com/abcd1.jpg"},
        {"name": "Nezuko Kamado", "rarity": "Rare", "image": "https://i.imgur.com/abcd2.jpg"},
        {"name": "Shinobu Kocho", "rarity": "Uncommon", "image": "https://i.imgur.com/abcd3.jpg"},
    ]
}


# /harem command
async def harem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [
            InlineKeyboardButton(
                "📸 Collection",
                switch_inline_query_current_chat=f"user_slaves.{user_id}"
            ),
            InlineKeyboardButton(
                "💌 AMV",
                switch_inline_query_current_chat=f"amv.{user_id}"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌸 *Slave Harem* 🌸\nChoose an option:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# Inline query (for gallery)
async def harem_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    user_id_match = re.match(r"user_slaves\.(\d+)", query)

    results = []

    if user_id_match:
        user_id = int(user_id_match.group(1))
        harem = USER_HAREMS.get(user_id, [])

        for idx, char in enumerate(harem):
            results.append(
                InlineQueryResultPhoto(
                    id=str(idx),
                    photo_url=char["image"],
                    thumb_url=char["image"],
                    title=char["name"],
                    description=f"{char['rarity']} character",
                    caption=f"✨ {char['name']} | {char['rarity']} ✨"
                )
            )

    await update.inline_query.answer(results, cache_time=0, is_personal=True)


# Register handlers
def register_handlers(app):
    app.add_handler(CommandHandler("harem", harem_command))
    app.add_handler(InlineQueryHandler(harem_inline_query))
                                                  
