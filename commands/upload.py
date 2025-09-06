from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import json

WAIFU_DATA = "waifu_data/waifus.json"

async def upload_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /upload Name Series Rarity DropChance when used as a reply to an image."""
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("⚠️ Reply to a waifu image with:\n/upload <Name> <Series> <Rarity> <DropChance>")
        return

    if len(context.args) < 4:
        await update.message.reply_text("⚠️ Usage: /upload <Name> <Series> <Rarity> <DropChance>")
        return

    name = context.args[0]
    series = context.args[1].replace("-", " ")
    rarity = context.args[2]
    try:
        drop_chance = float(context.args[3])  # allow 5 or 5.0
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
        "image": file_id
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
  
