from telegram import Update
from telegram.ext import ContextTypes

from core.router import get_provider
from memory.user_memory import add_message
from interface.utils import split_message

ai = get_provider()


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "سلام! 👋\n\n"
        "من Atlas هستم 🤖\n"
        "آماده‌ام کمکت کنم 🚀"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return


    if not update.message.text:

        await update.message.reply_text(
            "فقط پیام متنی بفرست 🙂"
        )

        return


    user_input = update.message.text.strip()


    if not user_input:
        return


    user_id = update.effective_user.id


    try:

        # نمایش حالت تایپ کردن
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )


        # ذخیره پیام کاربر
        messages = add_message(
            user_id,
            "user",
            user_input
        )


        print(
            f"🧠 Using: {ai.current_name()}"
        )

        print(
            f"📦 Messages: {len(messages)}"
        )


        # گرفتن پاسخ Atlas
        answer = ai.chat(messages)


        # ذخیره پاسخ Atlas
        add_message(
            user_id,
            "assistant",
            answer
        )


        # ارسال جواب‌های طولانی در چند بخش
        for part in split_message(answer):

            await update.message.reply_text(
                part
            )


    except Exception as error:


        print(
            f"⚠️ Atlas Error: {error}"
        )


        await update.message.reply_text(
            f"⚠️ Atlas Error:\n{error}"
        )
