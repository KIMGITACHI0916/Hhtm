from db.models import get_leaderboard

def handle_leaderboard(update, context):
    leaderboard = get_leaderboard()
    msg = "Top Waifu Collectors:\n"
    for idx, (user_id, count) in enumerate(leaderboard, 1):
        msg += f"{idx}. User {user_id}: {count} waifus\n"
    update.message.reply_text(msg)
