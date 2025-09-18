import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers import (
    start,
    help_cmd,
    about,       
    stats,       
    broadcast,
    chat,
    users_cmd
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("about", about))     
    application.add_handler(CommandHandler("stats", stats))     
    application.add_handler(CommandHandler("users", users_cmd))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Chat (normal message)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
