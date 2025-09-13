from db.models import trade_slave, get_user_id_by_username

def handle_trade(update, context):
    user = update.effective_user
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /trade @user <slave_id>")
        return
    target_username = args[0].replace("@", "")
    slave_id = args[1]
    target_id = get_user_id_by_username(target_username)
    if not target_id:
        update.message.reply_text("User not found!")
        return
    success = trade_slave(user.id, target_id, slave_id)
    if success:
        update.message.reply_text(f"Trade request sent to @{target_username} for slave {slave_id}.")
    else:
        update.message.reply_text("Trade failed. Check ownership or slave ID.")