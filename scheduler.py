# scheduler.py
import asyncio
from utils.waifu_picker import pick_random_waifu
from db.models import groups

current_drop = {}      # chat_id -> waifu
running_tasks = {}     # chat_id -> asyncio.Task

TEASER = "Ｃʜᴀʀᴀᴄᴛᴇʀ Ｄʀᴏᴘ Ｉɴᴄᴏᴍɪɴɢ！"
DROP_MSG = (
    "✨ 𝑨 𝑾𝒂𝒊𝒇𝒖 𝑨𝒑𝒑𝒆𝒂𝒓𝒆𝒅！✨\n"
    "🪄 𝑮𝒓𝒂𝒃 𝒊𝒕 𝒘𝒊𝒕𝒉 /grab name\n"
    "💥 𝑸𝒖𝒊𝒄𝒌！ 𝑶𝒕𝒉𝒆𝒓𝒔 𝒘𝒂𝒊𝒕𝒊𝒏𝒈..."
)

# --- Drop ek waifu ---
async def drop_waifu(bot, chat_id):
    try:
        waifu = pick_random_waifu()
        if not waifu:
            return

        current_drop[chat_id] = waifu
        await bot.send_message(chat_id, TEASER)
        await asyncio.sleep(10)

        await bot.send_photo(
            chat_id,
            photo=waifu["image"],
            caption=f"{DROP_MSG}\n\n🎨 {waifu['name']} ({waifu['rarity']})\n{waifu['desc']}"
        )

        await asyncio.sleep(300)
        if chat_id in current_drop:
            await bot.send_message(chat_id, f"⏳ Time’s up! {waifu['name']} escaped…")
            del current_drop[chat_id]

    except Exception as e:
        print(f"[Drop Error] {chat_id}: {e}")


# --- Group scheduler loop ---
async def group_scheduler(app, chat_id):
    await asyncio.sleep(5)
    while True:
        await drop_waifu(app.bot, chat_id)
        await asyncio.sleep(600)   # 10 min gap


# --- Start scheduler for group ---
def start_group_scheduler(app, chat_id):
    if chat_id in running_tasks:  # already running
        return
    task = asyncio.create_task(group_scheduler(app, chat_id))
    running_tasks[chat_id] = task
    print(f"[Scheduler] Started in {chat_id}")


# --- Stop scheduler for group ---
def stop_group_scheduler(chat_id):
    task = running_tasks.get(chat_id)
    if task:
        task.cancel()
        del running_tasks[chat_id]
        print(f"[Scheduler] Stopped in {chat_id}")
        
