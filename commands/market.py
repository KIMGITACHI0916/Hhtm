from db.models import get_market_items

def handle_market(update, context):
    items = get_market_items()
    msg = "Marketplace:\n"
    for item in items:
        msg += f"{item['id']}: {item['name']} - {item['price']} coins\n"
    update.message.reply_text(msg)
