# commands/upload.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import os
import re
import json
import pathlib

# Owner ID
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# JSON file
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
WAIFU_DATA = BASE_DIR / "waifu_data" / "waifus.json"
WAIFU_DATA.parent.mkdir(parents=True, exist_ok=True)
if not WAIFU_DATA.exists():
    WAIFU_DATA.write_text("[]")  # initialize empty list

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

    name = matches[0].strip()
    series = matches[1].strip()
    rarity = matches[2].strip()
    try:
        waifu_id = int(matches[3].strip())
        drop_chance = float(matches[4].strip())
    except ValueError:
        await update.message.reply_text("⚠️ ID must be integer, DropChance must be number.")
        return

    # Get photo file ID
    file_id = None
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        file_id = update.message.reply_to_message.photo[-1].file_id
    elif len(matches) >= 6:
        file_id = matches[5].strip()

    if not file_id:
        await update.message.reply_text(
            "⚠️ Please reply to a photo or provide a valid Telegram file ID."
        )
        return

    # Load existing waifus
    try:
        waifus = json.loads(WAIFU_DATA.read_text())
    except json.JSONDecodeError:
        waifus = []

    # Check duplicate ID
    if any(w["id"] == waifu_id for w in waifus):
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

    # Save back to JSON
    WAIFU_DATA.write_text(json.dumps(waifus, indent=4))

    await update.message.reply_text(
        f"✅ Added {name} ({series}) | Rarity: {rarity} | ID: {waifu_id} | Drop Chance: {drop_chance}%"
    )

def get_upload_handler():
    return CommandHandler("upload", upload_waifu)
    
