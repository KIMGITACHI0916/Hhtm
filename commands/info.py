# /app/commands/info.py

async def handle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    count = get_waifu_count(user_id)  # however you calculate it
    await update.message.reply_text(f"You have {count} waifus in your harem.")
    
