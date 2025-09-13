import time
from db.models import get_last_daily, set_last_daily, add_coins

DAILY_REWARD = 100  # Amount of coins for daily reward

def handle_daily(update, context):
    user = update.effective_user
    last_claim = get_last_daily(user.id)
    current_time = int(time.time())
    if last_claim and current_time - last_claim < 86400:
        update.message.reply_text("You've already claimed your daily reward today!")
    else:
        add_coins(user.id, DAILY_REWARD)
        set_last_daily(user.id, current_time)
        update.message.reply_text(f"You claimed {DAILY_REWARD} coins as your daily reward!")