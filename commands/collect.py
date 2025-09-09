from telegram import Update
from telegram.ext import ContextTypes
from scheduler import current_drop

# Track which waifu has already been collected (avoid double grab)
collected = set()

async def handle_collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_drop, collected

    if not current_drop.get("waifu"):
        await update.message.reply_text("❌ No waifu to grab right now!")
        return

    waifu = current_drop["waifu"]

    # Waifu already collected?
    if waifu["id"] in collected:
        await update.message.reply_text("⚠️ This waifu has already been grabbed!")
        return

    # User input check
    if len(context.args) == 0:
        await update.message.reply_text("ℹ️ Usage: /grab <waifu name>")
        return

    guess_name = " ".join(context.args).strip().lower()
    if guess_name != waifu["name"].lower():
        await update.message.reply_text("❌ Wrong name! Try again.")
        return

    # Mark as collected
    collected.add(waifu["id"])

    username = (
        f"@{update.effective_user.username}"
        if update.effective_user.username
        else update.effective_user.full_name
    )

    # Success message
    msg = (
        "🌸 Waifu Collection Update 🌸\n\n"
        f"💖 Character: {waifu['name']}\n"
        f"🎬 From: {waifu.get('desc', 'Unknown')}\n"
        f"💎 Rarity: {waifu.get('rarity', 'Unknown')}\n"
        f"🆔 Id: {waifu['id']}\n\n"
        f"📌 Grabbed by ➝ {username}"
    )

    await update.message.reply_text(msg)
    
