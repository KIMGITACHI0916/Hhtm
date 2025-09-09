# scheduler.py
import asyncio
from utils.waifu_picker import pick_random_waifu
from db.models import groups

current_drop = {}  # chat_id -> waifu

TEASER_MSG = "Ｃʜᴀʀᴀᴄᴛᴇʀ Ｄʀᴏᴘ Ｉɴᴄᴏᴍɪɴɢ！"
DROP_MSG = (
    "✨ 𝑨 𝑾𝒂𝒊𝒇𝒖 𝑨𝒑𝒑𝒆𝒂𝒓𝒆𝒅！✨\n"
    "🪄 𝑮𝒓𝒂𝒃 𝒊𝒕 𝒘𝒊𝒕𝒉 /grab name 𝒂𝒏𝒅 𝒎𝒂𝒌𝒆 𝒊𝒕 𝒚𝒐𝒖𝒓𝒔！\n"
    "💥 𝑸𝒖𝒊𝒄𝒌！𝑶𝒕𝒉𝒆𝒓𝒔 𝒂𝒓𝒆 𝒘𝒂𝒊𝒕𝒊𝒏𝒈 𝒕𝒐 𝒈𝒓𝒂𝒃 𝒊𝒕 𝒂𝒘𝒂𝒙！！！"
)

# --- Drop one waifu ---
async def drop_waifu(bot, chat_id):
    try:
        waifu = pick_random_waifu()
        if not waifu:
            print(f"[Scheduler] No waifu for {chat_id}")
            return

        current_drop[chat_id] = waifu

        await bot.send_message(chat_id=chat_id, text=TEASER_MSG)
        await asyncio.sleep(10)  # teaser delay

        await bot.send_photo(
            chat_id=chat_id,
            photo=waifu["image"],
            caption=f"{DROP_MSG}\n\n🎨 {waifu['name']} ({waifu['rarity']})\n{waifu['desc']}"
        )

        await asyncio.sleep(300)  # 5 min grab window
        if chat_id in current_drop:
            await bot.send_message(chat_id=chat_id, text=f"⏳ Time’s up! {waifu['name']} escaped…")
            del current_drop[chat_id]

    except Exception as e:
        print(f"[Scheduler] Drop failed in {chat_id}: {e}")

# --- Global scheduler loop ---
async def start_scheduler(app):
    await asyncio.sleep(5)
    while True:
        all_groups = list(groups.find({}))
        for g in all_groups:
            asyncio.create_task(drop_waifu(app.bot, g["chat_id"]))
        await asyncio.sleep(600)  # 10 minutes interval
