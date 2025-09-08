# commands/upload.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import os
import re
import json

WAIFU_DATA = os.path.join(os.path.dirname(__file__), "..", "waifu_data", "waifus.json")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

async def upload_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("🚫 Only the owner can upload waifus.")
        return

    text = update.message.text
    matches = re.findall(r"\((.*?)\)", text)

    if len(matches) < 5:
        await update.message.reply_text(
            "⚠️ Usage: /upload (Name) (Series) (Rarity) (ID) (DropChance) [FileID]"
        )
        return

    name, series, rarity = matches[0].strip(), matches[1].strip(), matches[2].strip()
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

    # Image: reply to photo or optional FileID
    file_id = None
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo = update.message.reply_to_message.photo[-1]
        file_id = photo.file_id
    elif len(matches) >= 6:
        file_id = matches[5].strip()

    if not file_id:
        await update.message.reply_text("⚠️ Reply to a photo or provide a file ID.")
        return

    # Load JSON
    try:
        with open(WAIFU_DATA, "r") as f:
            waifus = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        waifus = []

    # Check duplicate ID
    if any(w.get("id") == waifu_id for w in waifus):
        await update.message.reply_text(f"⚠️ Waifu with ID {waifu_id} already exists!")
        return

    # Add new waifu
    new_waifu = {
        "id": waifu_id,
        "name": name,
        "series": series,
        "rarity": rarity,
        "drop_chance": drop_chance,
        "desc": f"From {series}",
        "image": file_id,
    }
    waifus.append(new_waifu)

    # Save JSON
    with open(WAIFU_DATA, "w") as f:
        json.dump(waifus, f, indent=4)

    await update.message.reply_text(
        f"✅ Added {name} ({series}) | Rarity: {rarity} | ID: {waifu_id} | Drop Chance: {drop_chance}%"
    )

def get_upload_handler():
    return CommandHandler("upload", upload_waifu)
    
