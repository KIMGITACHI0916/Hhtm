from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import json
import os
import re

WAIFU_DATA = os.path.join(os.path.dirname(__file__), "..", "waifu_data", "waifus.json")

async def upload_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /upload (Name) (Series) (Rarity) (DropChance) when used as a reply to an image."""

    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "⚠️ Reply to a waifu image with:\n/upload (Name) (Series) (Rarity) (DropChance)"
        )
        return

    # Extract things inside ( )
    text = update.message.text
    matches = re.findall(r"\((.*?)\)", text)

    if len(matches) < 4:
        await update.message.reply_text(
            "⚠️ Usage: /upload (Name) (Series) (Rarity) (DropChance)"
        )
        return

    name = matches[0].strip()
    series = matches[1].strip()
    rarity = matches[2].strip()
    try:
        drop_chance = float(matches[3].strip())
    except ValueError:
        await update.message.reply_text("⚠️ DropChance must be a number.")
        return

    photo = update.message.reply_to_message.photo[-1]  # best quality
    file_id = photo.file_id

    new_waifu = {
        "name": name,
        "series": series,
        "rarity": rarity,
        "drop_chance": drop_chance,
        "desc": f"From {series}",
        "image": file_id,
    }

    # Save into JSON
    try:
        with open(WAIFU_DATA, "r") as f:
            waifus = json.load(f)
    except FileNotFoundError:
        waifus = []

    waifus.append(new_waifu)
    with open(WAIFU_DATA, "w") as f:
        json.dump(waifus, f, indent=4)

    await update.message.reply_text(
        f"✅ Added {name} ({series}) | Rarity: {rarity} | Drop Chance: {drop_chance}%"
    )

def get_upload_handler():
    return CommandHandler("upload", upload_waifu)
    
