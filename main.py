
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)
from handlers import (
    start,
    help_cmd,
    about_cmd,
    stats_cmd,
    broadcast_cmd,
    chat_with_ai
)
from config import BOT_TOKEN

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("about", about_cmd))
    application.add_handler(CommandHandler("stats", stats_cmd))
    application.add_handler(CommandHandler("broadcast", broadcast_cmd))
    

    # Chat with AI on every text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_ai))

    # Run bot
    logger.info("🤖 Bot started...")
    application.run_polling()


if __name__ == "__main__":
    main()
