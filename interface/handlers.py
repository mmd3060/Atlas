from telegram import Update
from telegram.ext import ContextTypes

from core.router import get_provider
from memory.chat_memory import add_message


ai = get_provider()


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "سلام محمد! 👋\n\n"
        "من Atlas هستم.\n"
        "آماده‌ام کمکت کنم 🚀"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # جلوگیری از پیام‌های بدون متن
    if not update.message:
        return

    if not update.message.text:
        await update.message.reply_text(
            "فقط پیام متنی بفرست محمد 🙂"
        )
        return


    user_input = update.message.text.strip()


    if not user_input:
        return


    try:

        messages = add_message(
            "user",
            user_input
        )


        answer = ai.chat(
            messages
        )


        add_message(
            "assistant",
            answer
        )


        await update.message.reply_text(
            answer
        )


    except Exception as error:

        print(
            f"⚠️ Atlas Error: {error}"
        )

        await update.message.reply_text(
            f"⚠️ Atlas Error:\n{error}"
        )
