# commands/upload.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from db.models import waifus  # MongoDB collection
import os
import re

# ✅ Owner ID from env
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

async def upload_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /upload (Name) (Series) (Rarity) (ID) [FileID]
    Matches waifu_picker.py fields exactly:
    - name
    - series (used for desc)
    - rarity
    - id
    - image
    """

    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("🚫 Only the owner can upload waifus.")
        return

    text = update.message.text
    matches = re.findall(r"\((.*?)\)", text)

    if len(matches) < 4:
        await update.message.reply_text(
            "⚠️ Usage: /upload (Name) (Series) (Rarity) (ID) [FileID]"
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

    # Get image: reply to photo or optional file ID
    file_id = None
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo = update.message.reply_to_message.photo[-1]  # best quality
        file_id = photo.file_id
    elif len(matches) >= 5:
        file_id = matches[4].strip()
    
    if not file_id:
        await update.message.reply_text(
            "⚠️ Please reply to a photo or provide a valid Telegram file ID."
        )
        return

    # Check for duplicate ID
    if waifus.find_one({"id": waifu_id}):
        await update.message.reply_text(f"⚠️ Waifu with ID {waifu_id} already exists!")
        return

    # Prepare waifu document exactly like waifu_picker.py expects
    new_waifu = {
        "id": waifu_id,
        "name": name,
        "rarity": rarity,
        "desc": f"From {series}",
        "image": file_id,
    }

    # Insert into MongoDB
    waifus.insert_one(new_waifu)

    await update.message.reply_text(
        f"✅ Added {name} | Rarity: {rarity} | ID: {waifu_id}"
    )

def get_upload_handler():
    return CommandHandler("upload", upload_waifu)
    
