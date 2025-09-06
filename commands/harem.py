from db.models import get_harem

def handle_harem(update, context):
    user = update.effective_user
    waifus = get_harem(user.id)
    if waifus:
        update.message.reply_text(f"Your harem: {', '.join(waifus)}")
    else:
        update.message.reply_text("Your harem is empty! Collect a waifu with /collect.")
