from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from ai import ask_ai
from database import add_user, get_all_users

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "Unknown")
    await update.message.reply_text("👋 Namaste! Main AI bot hoon, aap mujhse baat kar sakte ho.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "Unknown")
    user_message = update.message.text
    reply = ask_ai(user_message)
    await update.message.reply_text(reply)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sirf admin broadcast kar sakta hai.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message = " ".join(context.args)
    users = get_all_users()
    count = 0

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 {message}")
            count += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")
