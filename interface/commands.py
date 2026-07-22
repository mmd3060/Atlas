from stats.token_tracker import get_usage_report
from core.router import get_provider


async def usage_command(update, context):

    await update.message.reply_text(
        get_usage_report()
    )


async def status_command(update, context):

    ai = get_provider()

    text = (
        "🤖 Atlas Status\n\n"
        f"🧠 Provider: {ai.current_name()}\n"
        "💾 Memory: Active\n"
        f"👤 User ID: {update.effective_user.id}\n"
        "🚀 Status: Online"
    )

    await update.message.reply_text(text)


async def model_command(update, context):

    ai = get_provider()

    model = getattr(ai.current_provider, "model", "Unknown")

    await update.message.reply_text(
        f"📦 Current Model:\n{model}"
    )


async def clear_command(update, context):

    await update.message.reply_text(
        "🚧 این قابلیت هنوز در حال توسعه است."
    )
