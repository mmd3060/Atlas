import logging

from telegram import Update
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from interface.config import BOT_TOKEN
from interface.handlers import (
    start_command,
    handle_message,
)


# Telegram error logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        f"⚠️ Telegram Error: {context.error}"
    )


def main():

    # Better connection settings
    request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=30,
        write_timeout=30,
        pool_timeout=30,
    )


    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )


    # Commands

    app.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )


    # Normal messages

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )


    # Error handling

    app.add_error_handler(
        error_handler
    )


    print(
        "📱 Atlas Telegram Bot Online 🚀"
    )


    try:

        app.run_polling(
            drop_pending_updates=True
        )


    except KeyboardInterrupt:

        print(
            "\n🛑 Telegram Bot stopped"
        )


if __name__ == "__main__":
    main()
