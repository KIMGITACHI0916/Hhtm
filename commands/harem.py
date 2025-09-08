# commands/harem.py
from db.models import get_harem
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes

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

async def handle_harem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    harem = get_harem(user_id)

    if not harem:
        await update.message.reply_text("You don’t have any waifus yet 😢")
        return

    # Group by series
    series_map = defaultdict(list)
    for w in harem:
        rarity = RARITY_EMOJIS.get(w.get("rarity"), "◇")
        series_map[w.get("series", "Unknown")].append(
            f"◇ {rarity} {w['id']} {w['name']} ×{w['count']}"
        )

    # Build response
    response = []
    for series, waifus in series_map.items():
        response.append(f"{series} {len(waifus)}/{count_total_in_series(series)}")
        response.extend(waifus)

    await update.message.reply_text("\n".join(response))

def count_total_in_series(series_name: str) -> int:
    # Optional: lookup how many total characters exist in that series
    # For now, return placeholder (e.g. 100)
    return 100
    
