import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from core.router import get_provider
from memory.user_memory import add_message

from interface.utils import (
    split_message,
    typing_indicator,
)


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "سلام محمد! 👋\n\n"
        "من Atlas هستم 🤖\n"
        "آماده‌ام کمکت کنم 🚀"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
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

        # Smart Router انتخاب Provider
        ai = get_provider(
            user_input
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


        # نمایش typing تا پایان پاسخ
        stop_event = asyncio.Event()


        typing_task = asyncio.create_task(
            typing_indicator(
                update,
                stop_event
            )
        )


        try:

            # جلوگیری از قفل شدن ربات
            answer = await asyncio.to_thread(
                ai.chat,
                messages
            )


        finally:

            # توقف typing
            stop_event.set()

            await typing_task



        # ذخیره پاسخ Atlas
        add_message(
            user_id,
            "assistant",
            answer
        )


        # ارسال پاسخ تکه‌ای
        for part in split_message(answer):

            await update.message.reply_text(
                part
            )


    except Exception as error:


        print(
            f"⚠️ Atlas Error: {error}"
        )


        await update.message.reply_text(
            "⚠️ یک خطا در Atlas رخ داد.\n"
            f"{error}"
        )
