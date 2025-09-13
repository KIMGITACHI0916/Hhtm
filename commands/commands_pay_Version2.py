from db.models import get_wallet_balance, add_coins, remove_coins

def handle_pay(update, context):
    user = update.effective_user
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /pay @user <amount>")
        return
    target_username = args[0].replace("@", "")
    amount = int(args[1])
    if get_wallet_balance(user.id) < amount:
        update.message.reply_text("Not enough coins!")
        return
    target_id = get_user_id_by_username(target_username)
    if not target_id:
        update.message.reply_text("User not found!")
        return
    remove_coins(user.id, amount)
    add_coins(target_id, amount)
    update.message.reply_text(f"Sent {amount} coins to @{target_username}.")