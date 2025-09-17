
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID, RATE_LIMIT_PER_MINUTE
from ai import ask_ai
from database import add_user, get_all_users, is_banned, ban_user, unban_user, record_message, count_messages_last_minute
from utils import allowed_by_inmemory_rate

logger = logging.getLogger(__name__)

# Helper to chunk long text (Telegram limit ~4096)
def _chunk_text(text: str, limit: int = 4000):
    return [text[i:i+limit] for i in range(0, len(text), limit)]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "")
    await update.message.reply_text(
        "👋 Namaste! Main Iqra Chat Bot hoon.\n"
        "Use /help to see available commands. Bas message bhejo — main AI se reply karunga."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🧾 Commands:\n\n"
        "/start - Welcome\n"
        "/help - This message\n"
        "/about - Bot info\n"
        "/stats - (Admin) total users\n"
        "/users - (Admin) list user IDs\n"
        "/broadcast <message> - (Admin) send broadcast\n"
        "/ban <user_id> [reason] - (Admin) ban user\n"
        "/unban <user_id> - (Admin) unban user\n\n"
        "Normal message bhejo aur main AI se reply karunga."
    )
    await update.message.reply_text(help_text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 Iqra Chat Bot\n"
        "AI-powered Telegram bot (GPT)\n"
        "Features: AI chat, admin broadcast, user DB, ban/unban, rate-limiting.\n"
        "Repo: https://github.com/mosameer2098-ship-it/Iqra-chat-bot"
    )
    await update.message.reply_text(about_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sirf admin dekh sakta hai.")
        return
    users = get_all_users()
    await update.message.reply_text(f"👥 Total registered users: {len(users)}")

async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sirf admin dekh sakta hai.")
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("No registered users yet.")
        return
    users_str = "\n".join(str(u) for u in users)
    for chunk in _chunk_text(users_str, 4000):
        await update.message.reply_text(chunk)

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sirf admin ye kar sakta hai.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id> [reason]")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user_id. Use numeric user id.")
        return
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    ban_user(user_id, reason)
    await update.message.reply_text(f"✔️ Banned user {user_id}. Reason: {reason}")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sirf admin ye kar sakta hai.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user_id. Use numeric user id.")
        return
    unban_user(user_id)
    await update.message.reply_text(f"✔️ Unbanned user {user_id}.")

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
        except Exception as e:
            # user might have blocked bot or error — skip
            logger.debug("Broadcast skip %s: %s", user_id, e)
    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Main chat handler
    user = update.effective_user
    user_id = user.id
    text = update.message.text or ""

    # Add user to DB
    add_user(user_id, user.username or "")

    # Ban check
    if is_banned(user_id):
        await update.message.reply_text("❌ You are banned and cannot use this bot.")
        return

    # Rate limit: first in-memory check
    if not allowed_by_inmemory_rate(user_id):
        await update.message.reply_text(f"⏱️ Rate limit: Max {RATE_LIMIT_PER_MINUTE} messages per minute. Try again later.")
        return

    # Record message (DB) & check DB-based rate (extra layer)
    record_message(user_id, text)
    recent_count = count_messages_last_minute(user_id)
    if recent_count > RATE_LIMIT_PER_MINUTE + 5:  # small tolerance
        await update.message.reply_text(f"⏱️ You're sending too many messages ({recent_count} in last minute). Please slow down.")
        return

    # Ask AI
    try:
        reply = ask_ai(text, user_id=user_id)
    except Exception as e:
        logger.exception("AI request failed")
        reply = "⚠️ AI error."
    # chunk reply if too long
    for chunk in _chunk_text(reply, 4000):
        await update.message.reply_text(chunk)
