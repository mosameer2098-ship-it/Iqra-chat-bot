from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from ai import ask_ai
from database import add_user, get_all_users

# small helper: bahut lamba text chunk karne ke liye (telegram ~4096 char limit)
def _chunk_text(text: str, limit: int = 4000):
    return [text[i:i+limit] for i in range(0, len(text), limit)]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "Unknown")

    keyboard = [
        [
            InlineKeyboardButton("📢 Join Channel", url="https://t.me/rolllexxxx_support"),
            InlineKeyboardButton("👥 Support Group", url="https://t.me/best_friends_chatting_zone0"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Namaste! Main Iqra Chat Bot hoon.\n\nMeri commands dekhne ke liye /help type karo.\nAur neeche diye gaye links join karo:",
        reply_markup=reply_markup
    )

# /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🧾 Commands:\n\n"
        "/start - Welcome\n"
        "/help - This message\n"
        "/about - Bot info\n"
        "/stats - (Admin) total users\n"
        "/users - (Admin) list user IDs\n"
        "/broadcast <message> - (Admin) send broadcast\n\n"
        "Normal message bhejo aur main AI se reply karunga."
    )
    await update.message.reply_text(help_text)

# /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 *Iqra Chat Bot*\n"
        "AI-powered Telegram bot (GPT)\n"
        "Features: AI chat, admin broadcast, user DB, ban/unban.\n\n"
        "Repo: [GitHub](https://github.com/mosameer2098-ship-it/Iqra-chat-bot)"
    )

    keyboard = [
        [
            InlineKeyboardButton("📢 Join Channel", url="https://t.me/rolllexxxx_support"),
            InlineKeyboardButton("👥 Support Group", url="https://t.me/best_friends_chatting_zone0"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        about_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# /stats (admin only)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sirf admin dekh sakta hai.")
        return
    users = get_all_users()
    await update.message.reply_text(f"👥 Total registered users: {len(users)}")

# /users (admin only) - sends user IDs (chunked if zaroorat ho)
async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sirf admin dekh sakta hai.")
        return

    users = get_all_users()
    if not users:
        await update.message.reply_text("No registered users yet.")
        return

    users_str = "\n".join(str(u) for u in users)
    chunks = _chunk_text(users_str, 4000)
    for chunk in chunks:
        await update.message.reply_text(chunk)

# AI chat handler
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "Unknown")
    user_message = update.message.text
    reply = ask_ai(user_message)
    await update.message.reply_text(reply)

# Admin broadcast
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
            # skip users we can't message (blocked, etc.)
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")
