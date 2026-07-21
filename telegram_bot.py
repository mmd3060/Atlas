import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from core.router import get_provider

load_dotenv()

ai = get_provider()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    messages = [
        {
            "role": "user",
            "content": user_text
        }
    ]

    answer = ai.chat(messages)

    await update.message.reply_text(answer)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Atlas Telegram Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
