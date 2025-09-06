from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from telegram import Bot
from utils.waifu_picker import pick_random_waifu

current_waifu = None

async def drop_waifu(bot: Bot, chat_id: int):
    global current_waifu
    try:
        current_waifu = pick_random_waifu()
        await bot.send_photo(
            chat_id=chat_id,
            photo=current_waifu["image"],
            caption=f"Waifu Drop! {current_waifu['name']} ({current_waifu['rarity']})\n{current_waifu['desc']}"
        )
    except Exception as e:
        print(f"Waifu drop failed: {e}")

def start_scheduler(bot: Bot, chat_id: int):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(drop_waifu(bot, chat_id)), 'interval', seconds=30)
    scheduler.start()
    
