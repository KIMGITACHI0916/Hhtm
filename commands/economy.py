# commands/economy.py
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# --- Command functions ---
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎁 You claimed your daily reward! (+100 coins)")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Your wallet balance: 500 coins")

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /pay @user <amount>")
        return
    await update.message.reply_text(f"✅ Sent {context.args[1]} coins to {context.args[0]}")

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /trade @user <slave_id>")
        return
    await update.message.reply_text(f"🔄 Trade request sent to {context.args[0]} for slave ID {context.args[1]}")

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /give @user <slave_id>")
        return
    await update.message.reply_text(f"🎁 Gave slave ID {context.args[1]} to {context.args[0]}")

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏪 Welcome to the marketplace! (feature coming soon)")

# --- Register handlers ---
def get_economy_handlers():
    return [
        CommandHandler("daily", daily),
        CommandHandler("wallet", wallet),
        CommandHandler("pay", pay),
        CommandHandler("trade", trade),
        CommandHandler("give", give),
        CommandHandler("market", market),
    ]
  
