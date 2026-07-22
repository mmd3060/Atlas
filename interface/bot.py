import logging

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

from interface.commands import (
    usage_command,
    status_command,
    model_command,
    clear_command,
)


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
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


    # ========= Commands =========

    app.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )

    app.add_handler(
        CommandHandler(
            "usage",
            usage_command
        )
    )

    app.add_handler(
        CommandHandler(
            "status",
            status_command
        )
    )

    app.add_handler(
        CommandHandler(
            "model",
            model_command
        )
    )

    app.add_handler(
        CommandHandler(
            "clear",
            clear_command
        )
    )

    # ========= Chat =========

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    # ========= Errors =========

    app.add_error_handler(
        error_handler
    )

    print("=" * 45)
    print("🤖 Atlas Telegram Interface")
    print("✅ Status : ONLINE")
    print("📡 Mode   : Polling")
    print("=" * 45)

    try:

        app.run_polling(
            drop_pending_updates=True
        )

    except KeyboardInterrupt:

        print(
            "\n🛑 Atlas Telegram Bot Stopped"
        )


if __name__ == "__main__":
    main()
