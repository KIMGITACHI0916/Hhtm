from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from utils.waifu_picker import pick_random_waifu
import random

current_waifu = None

def drop_waifu(bot: Bot, chat_id: int):
    global current_waifu
    try:
        current_waifu = pick_random_waifu()
        bot.send_photo(
            chat_id=chat_id,
            photo=current_waifu["image"],
            caption=f"Waifu Drop! {current_waifu['name']} ({current_waifu['rarity']})\n{current_waifu['desc']}"
        )
    except Exception as e:
        print(f"Waifu drop failed: {e}")

def start_scheduler(bot: Bot, chat_id: int):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: drop_waifu(bot, chat_id), 'interval', seconds=30)  # drop every 30 sec
    scheduler.start()
    