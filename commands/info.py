from db.models import get_harem

def handle_info(update, context):
    user = update.effective_user
    harem = get_harem(user.id)
    count = len(harem)
    update.message.reply_text(f"You have {count} waifus in your harem.")
