# commands/waifulist.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from db.models import waifus  # MongoDB collection

async def waifulist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows how many waifus exist in the bot database"""
    all_waifus = list(waifus.find({}))

    if not all_waifus:
        await update.message.reply_text("⚠️ No waifus found in the database.")
        return

    total = len(all_waifus)

    # Optional: count per rarity
    rarity_counts = {}
    for w in all_waifus:
        rarity = w.get("rarity", "Unknown")
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1

    message = f"📚 Total Waifus: {total}\n\n"
    message += "🎨 Rarity Distribution:\n"
    for r, count in sorted(rarity_counts.items(), key=lambda x: x[1], reverse=True):
        message += f"• {r}: {count}\n"

    await update.message.reply_text(message)

def get_waifulist_handler():
    from telegram.ext import CommandHandler
    return CommandHandler("waifulist", waifulist)
    
