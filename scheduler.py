# scheduler.py
import asyncio
from telegram import Update
from utils.waifu_picker import pick_random_waifu
from db.models import groups, active_drops

TEASER_MSG = "Ｃʜᴀʀᴀᴄᴛᴇʀ Ｄʀᴏᴘ Ｉɴᴄᴏᴍɪɴɢ！"
DROP_MSG = (
    "✨ 𝑨 𝑾𝒂𝒊𝒇𝒖 𝑨𝒑𝒑𝒆𝒂𝒓𝒆𝒅！✨\n"
    "🪄 𝑮𝒓𝒂𝒃 𝒊𝒕 𝒘𝒊𝒕𝒉 /grab name 𝒂𝒏𝒅 𝒎𝒂𝒌𝒆 𝒊𝒕 𝒚𝒐𝒖𝒓𝒔！\n"
    "💥 𝑸𝒖𝒊𝒄𝒌！𝑶𝒕𝒉𝒆𝒓𝒔 𝒂𝒓𝒆 𝒘𝒂𝒊𝒕𝒊𝒏ɢ 𝒕𝒐 𝒈𝒓𝒂𝒃 𝒊𝒕 𝒂𝒘𝒂𝒚！！！"
)

# Track currently active drops per chat
current_drop = {}

async def drop_waifu(bot, chat_id: int):
    try:
        waifu = pick_random_waifu()
        if not waifu:
            print(f"[Scheduler] No waifu for {chat_id}")
            return

        current_drop[chat_id] = {"waifu": waifu}
        active_drops.update_one(
            {"chat_id": chat_id},
            {"$set": {"waifu": waifu}},
            upsert=True
        )

        await bot.send_message(chat_id=chat_id, text=TEASER_MSG)
        await asyncio.sleep(10)

        await bot.send_photo(chat_id=chat_id, photo=waifu["image"], caption=DROP_MSG)
        await asyncio.sleep(300)  # 5 min for grabs

        # Time up
        drop = active_drops.find_one({"chat_id": chat_id})
        if drop:
            await bot.send_message(chat_id=chat_id, text=f"⏳ Time’s up! {waifu['name']} escaped…")
            active_drops.delete_one({"chat_id": chat_id})
            del current_drop[chat_id]

    except Exception as e:
        print(f"[Scheduler] Drop failed in {chat_id}: {e}")

async def start_scheduler(app):
    await asyncio.sleep(5)
    while True:
        all_groups = list(groups.find({}))
        print(f"[DEBUG] Groups in DB: {[g['chat_id'] for g in all_groups]}")

        for g in all_groups:
            asyncio.create_task(drop_waifu(app.bot, g["chat_id"]))

        await asyncio.sleep(600)  # 10 min interval
