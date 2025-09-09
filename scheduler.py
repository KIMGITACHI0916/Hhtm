import asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes, ChatMemberHandler
from utils.waifu_picker import pick_random_waifu
from db.models import groups  # store groups in DB

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
        await asyncio.sleep(10)

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


# --- Global scheduler ---
async def start_scheduler(app: Application):
    """Drop waifus in ALL groups every 10 min"""
    await asyncio.sleep(5)  # wait for bot startup
    while True:
        all_groups = list(groups.find({}))
        for g in all_groups:
            asyncio.create_task(drop_waifu(app.bot, g["chat_id"]))
        await asyncio.sleep(600)  # 10 minutes


# --- Track when bot is added/removed ---
async def handle_new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Use my_chat_member for bot's own status updates
    chat_member_update = getattr(update, "my_chat_member", None)
    if not chat_member_update:
        return  # nothing to do

    chat = chat_member_update.chat
    new_status = chat_member_update.new_chat_member.status
    old_status = chat_member_update.old_chat_member.status

    # Bot added to a group
    if new_status in ["member", "administrator"] and chat.type in ["group", "supergroup"]:
        groups.update_one(
            {"chat_id": chat.id},
            {"$set": {"chat_id": chat.id, "title": chat.title}},
            upsert=True
        )
        print(f"[Scheduler] Added {chat.title} ({chat.id})")

    # Bot removed from a group
    elif old_status in ["member", "administrator"] and new_status == "left":
        groups.delete_one({"chat_id": chat.id})
        print(f"[Scheduler] Removed {chat.title} ({chat.id})")


# --- Add handlers function for bot.py ---
def add_handlers(app: Application):
    """Attach chat join/leave handler"""
    app.add_handler(ChatMemberHandler(handle_new_chat, ChatMemberHandler.MY_CHAT_MEMBER))
    
