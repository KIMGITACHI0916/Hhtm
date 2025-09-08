# commands/waifulist.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import json
import os

WAIFU_DATA = os.path.join(os.path.dirname(__file__), "..", "waifu_data", "waifus.json")

async def waifulist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows how many waifus exist in the bot database"""
    try:
        with open(WAIFU_DATA, "r") as f:
            waifus = json.load(f)
    except FileNotFoundError:
        await update.message.reply_text("⚠️ No waifus found in the database.")
        return

    if not waifus:
        await update.message.reply_text("⚠️ No waifus found in the database.")
        return

    # Count total waifus
    total = len(waifus)

    # Optional: count per rarity
    rarity_counts = {}
    for w in waifus:
        rarity = w.get("rarity", "Unknown")
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1

    message = f"📚 Total Waifus: {total}\n\n"
    message += "🎨 Rarity Distribution:\n"
    for r, count in sorted(rarity_counts.items(), key=lambda x: x[1], reverse=True):
        message += f"• {r}: {count}\n"

    await update.message.reply_text(message)

def get_waifulist_handler():
    return CommandHandler("waifulist", waifulist)
