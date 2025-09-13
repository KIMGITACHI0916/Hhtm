from db.models import get_wallet_balance

def handle_wallet(update, context):
    user = update.effective_user
    balance = get_wallet_balance(user.id)
    update.message.reply_text(f"Your wallet balance: {balance} coins.")