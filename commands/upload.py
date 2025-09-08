from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import json
import os
import re

# ✅ Owner ID from env
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

WAIFU_DATA = os.path.join(os.path.dirname(__file__), "..", "waifu_data", "waifus.json")

async def upload_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /upload (Name) (Series) (Rarity) (ID) (DropChance) when used as a reply to an image."""

    # ✅ Owner check
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("🚫 Only the owner can upload waifus.")
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "⚠️ Reply to a waifu image with:\n/upload (Name) (Series) (Rarity) (ID) (DropChance)"
        )
        return

    # Extract things inside ( )
    text = update.message.text
    matches = re.findall(r"\((.*?)\)", text)

    if len(matches) < 5:
        await update.message.reply_text(
            "⚠️ Usage: /upload (Name) (Series) (Rarity) (ID) (DropChance)"
        )
        return

    name = matches[0].strip()
    series = matches[1].strip()
    rarity = matches[2].strip()

    try:
        waifu_id = int(matches[3].strip())
    except ValueError:
        await update.message.reply_text("⚠️ ID must be an integer.")
        return

    try:
        drop_chance = float(matches[4].strip())
    except ValueError:
        await update.message.reply_text("⚠️ DropChance must be a number.")
        return

    photo = update.message.reply_to_message.photo[-1]  # best quality
    file_id = photo.file_id

    new_waifu = {
        "id": waifu_id,
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

    # Prevent duplicate ID
    if any(w.get("id") == waifu_id for w in waifus):
        await update.message.reply_text(f"⚠️ Waifu with ID {waifu_id} already exists!")
        return

    waifus.append(new_waifu)
    with open(WAIFU_DATA, "w") as f:
        json.dump(waifus, f, indent=4)

    await update.message.reply_text(
        f"✅ Added {name} ({series}) | Rarity: {rarity} | ID: {waifu_id} | Drop Chance: {drop_chance}%"
    )

def get_upload_handler():
    return CommandHandler("upload", upload_waifu)
    
