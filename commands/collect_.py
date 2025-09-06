from scheduler import current_waifu
from db.models import add_waifu_to_harem

def handle_collect(update, context):
    global current_waifu
    user = update.effective_user
    if current_waifu:
        add_waifu_to_harem(user.id, current_waifu["name"])
        update.message.reply_text(f"You collected {current_waifu['name']}!")
        current_waifu = None
    else:
        update.message.reply_text("No waifu to collect right now!")
