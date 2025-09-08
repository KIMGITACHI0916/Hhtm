# commands/waifulist.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import json
import os

WAIFU_DATA = os.path.join(os.path.dirname(__file__), "..", "waifu_data", "waifus.json")

async def waifulist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows how many waifus exist in the bot database, grouped by rarity."""
    try:
        with open(WAIFU_DATA, "r") as f:
            waifus = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        await update.message.reply_text("⚠️ No waifus found in the database.")
        return

    if not waifus:
        await update.message.reply_text("⚠️ No waifus found in the database.")
        return

    # Group waifus by rarity
    rarity_groups = {}
    for w in waifus:
        rarity = w.get("rarity", "Unknown")
        if rarity not in rarity_groups:
            rarity_groups[rarity] = []
        rarity_groups[rarity].append(f"{w.get('name', 'Unknown')} (ID: {w.get('id', 'N/A')})")

    message = f"📚 Total Waifus: {len(waifus)}\n\n🎨 Rarity Distribution:\n"

    # Optional: define order for rarities (low to high)
    rarity_order = ["⚪ Common", "🟢 Medium", "🟣 Rare", "🟡 Legendary",
                    "💮 Special Edition", "🔮 Limited Edition", "🎐 Celestial",
                    "💖 Valentine", "❄️ Winter", "💌 AMV"]

    for rarity in rarity_order:
        if rarity in rarity_groups:
            waifu_list = "\n  ".join(rarity_groups[rarity])
            message += f"• {rarity} ({len(rarity_groups[rarity])}):\n  {waifu_list}\n"

    await update.message.reply_text(message)

def get_waifulist_handler():
    return CommandHandler("waifulist", waifulist)
    
