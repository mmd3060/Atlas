from stats.token_tracker import get_usage_report


async def usage_command(update, context):

    await update.message.reply_text(
        get_usage_report()
    )
