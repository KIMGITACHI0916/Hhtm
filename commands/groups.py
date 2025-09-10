# commands/groups.py
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from db.models import groups

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_groups = list(groups.find({}))
    if not all_groups:
        await update.message.reply_text("⚠️ No groups registered in DB.")
        return

    msg = "📋 Registered Groups:\n\n"
    for g in all_groups:
        title = g.get("title", "Unknown")
        chat_id = g.get("chat_id")
        msg += f"• {title} (`{chat_id}`)\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

def get_groups_handler():
    return CommandHandler("groups", list_groups)
  
