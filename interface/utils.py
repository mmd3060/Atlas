import asyncio

from telegram import Update
from telegram.constants import ChatAction


async def typing_indicator(
    update: Update,
    stop_event: asyncio.Event,
):
    """
    ارسال وضعیت typing تا وقتی پاسخ آماده شود
    """

    while not stop_event.is_set():

        try:

            await update.effective_chat.send_action(
                ChatAction.TYPING
            )

        except Exception:
            pass


        try:

            await asyncio.wait_for(
                stop_event.wait(),
                timeout=4
            )

        except asyncio.TimeoutError:

            continue



def split_message(
    text,
    limit=4000
):
    """
    تقسیم پیام‌های طولانی برای محدودیت تلگرام
    """

    if len(text) <= limit:
        return [text]


    parts = []

    while len(text) > limit:

        cut = text[:limit]

        # تلاش برای شکستن از فاصله
        position = cut.rfind(" ")

        if position != -1:
            cut = text[:position]


        parts.append(cut)

        text = text[len(cut):]


    if text:
        parts.append(text)


    return parts
