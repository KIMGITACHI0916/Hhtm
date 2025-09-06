# scheduler.py
from telegram.ext import Application
from utils.waifu_picker import pick_random_waifu
import asyncio

current_waifu = None

async def drop_waifu(bot, chat_id):
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

async def start_scheduler(app: Application, chat_id: int):
    """Schedules waifu drops using the running event loop."""
    while True:
        await drop_waifu(app.bot, chat_id)
        await asyncio.sleep(30)  # drop every 30 seconds
