import asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes, ChatMemberHandler
from utils.waifu_picker import pick_random_waifu

current_drop = {}  # chat_id -> waifu

TEASER_MSG = "Ｃʜᴀʀᴀᴄᴛᴇʀ Ｄʀᴏᴘ Ｉɴᴄᴏᴍɪɴɢ！"
DROP_MSG = (
    "✨ 𝑨 𝑾𝒂𝒊𝒇𝒖 𝑨𝒑𝒑𝒆𝒂𝒓𝒆𝒅！✨\n"
    "🪄 𝑮𝒓𝒂𝒃 𝒊𝒕 𝒘𝒊𝒕𝒉 /grab name 𝒂𝒏𝒅 𝒎𝒂𝒌𝒆 𝒊𝒕 𝒚𝒐𝒖𝒓𝒔！\n"
    "💥 𝑶𝒕𝒉𝒆𝒓𝒔 𝒂𝒓𝒆 𝒘𝒂𝒊𝒕𝒊𝒏𝒈 𝒕𝒐 𝒈𝒓𝒂𝒃 𝒊𝒕 𝒂𝒘𝒂𝒚！！！"
)

# --- Messages ---
async def teaser_message(bot, chat_id):
    try:
        await bot.send_message(chat_id=chat_id, text=TEASER_MSG)
    except Exception as e:
        print(f"[Scheduler] Teaser send failed: {e}")

async def drop_waifu(bot, chat_id):
    try:
        waifu = pick_random_waifu()
        if not waifu:
            print("[Scheduler] No waifu returned")
            return

        current_drop[chat_id] = waifu

        await bot.send_photo(
            chat_id=chat_id,
            photo=waifu["image"],
            caption=f"{DROP_MSG}\n\n🎨 {waifu['name']} ({waifu['rarity']})\n{waifu['desc']}"
        )

        # 5 min collect window
        await asyncio.sleep(300)

        # if not collected
        if chat_id in current_drop:
            await bot.send_message(
                chat_id=chat_id,
                text=f"⏳ ᴛɪᴍᴇ’ꜱ ᴜᴘ! {waifu['name']} ᴇꜱᴄᴀᴘᴇᴅ…"
            )
            del current_drop[chat_id]

    except Exception as e:
        print(f"[Scheduler] Drop failed: {e}")

# --- Scheduler loop ---
async def start_scheduler(app: Application, chat_id: int):
    """Start waifu drop cycle for a group."""
    while True:
        await teaser_message(app.bot, chat_id)
        await asyncio.sleep(10)  # teaser wait

        # drop in background
        asyncio.create_task(drop_waifu(app.bot, chat_id))

        # wait for next drop (10 min interval)
        await asyncio.sleep(600)

# --- Auto-start when bot is added to a group ---
async def handle_new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.chat_member.chat
    new_status = update.chat_member.new_chat_member.status

    if new_status in ["member", "administrator"]:
        chat_id = chat.id
        asyncio.create_task(start_scheduler(context.application, chat_id))
        print(f"[Scheduler] Started waifu drops in chat {chat_id}")

def add_handlers(app: Application):
    """Attach the chat join handler to the bot."""
    app.add_handler(ChatMemberHandler(handle_new_chat, ChatMemberHandler.MY_CHAT_MEMBER))
    
