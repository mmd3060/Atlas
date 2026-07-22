from stats.token_tracker import get_usage_report
from core.router import get_provider
from core.capabilities import get_capabilities


async def usage_command(update, context):
    """نمایش مصرف توکن"""
    await update.message.reply_text(
        get_usage_report()
    )


async def status_command(update, context):
    """وضعیت فعلی Atlas"""

    ai = get_provider()

    provider = ai.current_name()
    model = getattr(
        ai.current_provider,
        "model",
        "Unknown"
    )

    text = (
        "🤖 Atlas Status\n\n"
        f"🟢 Status : Online\n"
        f"🧠 Provider : {provider}\n"
        f"📦 Model : {model}\n"
        f"💾 Memory : Active\n"
        f"👤 User ID : {update.effective_user.id}"
    )

    await update.message.reply_text(text)


async def model_command(update, context):
    """نمایش مدل فعلی"""

    ai = get_provider()

    model = getattr(
        ai.current_provider,
        "model",
        "Unknown"
    )

    await update.message.reply_text(
        f"📦 Current Model\n\n{model}"
    )


async def capabilities_command(update, context):
    """نمایش قابلیت‌های واقعی Atlas"""

    data = get_capabilities()

    active = "\n".join(
        f"✅ {item}"
        for item in data["active"]
    )

    developing = "\n".join(
        f"🛠 {item}"
        for item in data["developing"]
    )

    text = (
        "🤖 Atlas Capabilities\n\n"
        "📌 فعال:\n"
        f"{active}\n\n"
        "🚧 در حال توسعه:\n"
        f"{developing}"
    )

    await update.message.reply_text(text)


async def clear_command(update, context):
    """پاک کردن حافظه (فعلاً غیرفعال)"""

    await update.message.reply_text(
        "🚧 این قابلیت هنوز پیاده‌سازی نشده است."
    )
