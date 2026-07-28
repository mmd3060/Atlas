#!/usr/bin/env python3
"""
Atlas OS Telegram Bot — Voice, Text, Image, Tools Interface.

Features:
  - /start — Welcome
  - /status — System status
  - /tools — List available tools
  - /agents — List AI agents
  - /memory — Memory status
  - /search <query> — Web search
  - /code <python code> — Execute Python
  - /file <path> — Read file
  - Voice messages — Transcription (STT)
  - Image messages — Analysis (Vision)
"""

import os
import sys

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


def start_bot():
    """Start the Telegram bot."""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        print("Set it: TELEGRAM_BOT_TOKEN=your_token_here")
        return

    try:
        import telegram
        from telegram import Update, BotCommand
        from telegram.ext import (
            Application,
            CommandHandler,
            MessageHandler,
            filters,
            ContextTypes,
        )
    except ImportError:
        print("❌ python-telegram-bot not installed")
        print("Run: pip install python-telegram-bot")
        return

    from core.tools.tool_system import ToolSystem
    from core.tools.web_search import WebSearchTool
    from core.tools.file_manager import FileManager
    from core.tools.code_executor import CodeExecutor
    from core.agents.agent_manager import AgentManager
    from core.agents.self_modifying_agent import SelfModifyingAgent
    from core.intelligence.execution_engine import ExecutionEngine
    from core.memory.advanced_memory import AdvancedMemory
    from memory.chat_memory import add_message

    tool_system = ToolSystem()
    web_search = WebSearchTool()
    file_manager = FileManager()
    code_exec = CodeExecutor()
    agents = AgentManager()
    sma = SelfModifyingAgent()
    engine = ExecutionEngine()
    memory = AdvancedMemory()

    print("🤖 Atlas Telegram Bot Booting...")

    # ==========================================
    # Command Handlers
    # ==========================================

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome = (
            "⚡ Atlas OS — AI Operating System\n\n"
            "من اطلس هستم! یک سیستم‌عامل هوش مصنوعی.\n\n"
            "📌 دستورات:\n"
            "/status — وضعیت سیستم\n"
            "/tools — لیست ابزارها\n"
            "/agents — لیست ایجنت‌ها\n"
            "/search <query> — جستجوی وب\n"
            "/code <code> — اجرای کد\n"
            "/file <path> — خواندن فایل\n"
            "/memory — وضعیت حافظه\n\n"
            "💬 یا هر متنی بفرست تا با AI پاسخ بدم!\n"
            "🖼️ عکس بفرست تا تحلیلش کنم!\n"
            "🎤 صدا بفرست تا تبدیل به متن کنم!"
        )
        await update.message.reply_text(welcome)

    async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        status = (
            "⚡ Atlas OS Status\n\n"
            f"🧠 Provider: Gemini\n"
            f"🛠️ Tools: {len(tool_system.list_tools())} active\n"
            f"🤖 Agents: {len(agents.list_agents())}\n"
            f"💾 Memory: 3-Layer (Episodic+Semantic+Procedural)\n"
            f"🔧 Self-Modifying: Active\n"
        )
        await update.message.reply_text(status)

    async def cmd_tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
        tools = tool_system.list_tools()
        lines = ["🛠️ Atlas Tools:\n"]
        for name, info in tools.items():
            lines.append(f"  • {name}: {info['description']}")
        await update.message.reply_text("\n".join(lines))

    async def cmd_agents(update: Update, context: ContextTypes.DEFAULT_TYPE):
        agent_list = agents.list_agents()
        lines = ["🤖 Atlas Agents:\n"]
        for name, info in agent_list.items():
            lines.append(f"  • {name}: {info['role']}")
        await update.message.reply_text("\n".join(lines))

    async def cmd_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
        status = (
            "💾 Atlas Memory Systems\n\n"
            "  • Episodic: Events & conversations\n"
            "  • Semantic: Facts & knowledge\n"
            "  • Procedural: How-to knowledge\n"
            f"  • Episodic recent: {len(memory.episodic.get_recent(24))} events (24h)\n"
        )
        await update.message.reply_text(status)

    async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = " ".join(context.args) if context.args else ""
        if not query:
            await update.message.reply_text("Usage: /search <query>")
            return
        await update.message.reply_text(f"🔍 Searching: {query}...")
        result = web_search.search(query)
        answer = result.get("answer", "No results")
        await update.message.reply_text(f"🔍 Result:\n{answer}")

    async def cmd_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
        code = " ".join(context.args) if context.args else ""
        if not code:
            await update.message.reply_text("Usage: /code <python code>")
            return
        await update.message.reply_text("⚡ Executing...")
        result = code_exec.execute_python(code)
        output = result.get("stdout", "")
        error = result.get("error")
        if error:
            await update.message.reply_text(f"❌ Error:\n{error}")
        else:
            await update.message.reply_text(f"✅ Output:\n{output or '(no output)'}")

    async def cmd_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
        path = " ".join(context.args) if context.args else ""
        if not path:
            await update.message.reply_text("Usage: /file <path>")
            return
        result = file_manager.read_file(path)
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            content = result["content"][:3000]
            await update.message.reply_text(f"📄 {path} ({result['lines']} lines):\n```\n{content}\n```")

    # ==========================================
    # Message Handlers
    # ==========================================

    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle normal text messages with typing indicator."""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        user_msg = update.message.text
        try:
            add_message("user", user_msg)
            response = engine.execute(user_msg)
            add_message("assistant", response)
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages."""
        await update.message.reply_text("🖼️ Photo received! Vision analysis coming soon.")

    async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages: STT → Process → TTS → Send back."""
        try:
            await update.message.reply_text("🎤 دارم گوش می‌دم...")

            # ۱. دانلود فایل صوتی
            file = await update.message.voice.get_file()
            voice_path = os.path.join(tempfile.gettempdir(), "input.ogg")
            await file.download_to_drive(voice_path)
            print(f"📥 Voice downloaded: {voice_path}")

            # ۲. تبدیل به متن (STT)
            from core.interfaces.voice_gateway import VoiceGateway
            vg = VoiceGateway()
            stt_result = vg.speech_to_text(voice_path)
            text = stt_result.get("text", "")
            error = stt_result.get("error")

            if error:
                print(f"⚠️ STT Error: {error}")
                await update.message.reply_text(f"⚠️ خطا در تشخیص صدا:\n{error}")
                return

            if not text:
                await update.message.reply_text(
                    "⚠️ متوجه نشدم! لطفاً دوباره بگو یا متن بنویس."
                )
                return

            await update.message.reply_text(f"📝 شنیدم: {text}")

            # ۳. پردازش توسط مغز اطلس
            response_text = engine.execute(text)
            await update.message.reply_text(f"🤖 اطلس:\n{response_text}")

            # ۴. تبدیل پاسخ به صدا (TTS)
            try:
                voice_path = vg.text_to_speech(response_text)
                if voice_path and os.path.exists(voice_path):
                    with open(voice_path, "rb") as audio_file:
                        await update.message.reply_voice(voice=audio_file)
                else:
                    print("⚠️ TTS failed, text response sent instead")
            except Exception as tts_err:
                print(f"⚠️ TTS Error: {tts_err}")

        except Exception as e:
            print(f"❌ Voice Handler Error: {e}")
            await update.message.reply_text(f"❌ خطای پردازش صوت:\n{e}")

    # ==========================================
    # Build Application
    # ==========================================

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("tools", cmd_tools))
    app.add_handler(CommandHandler("agents", cmd_agents))
    app.add_handler(CommandHandler("memory", cmd_memory))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("code", cmd_code))
    app.add_handler(CommandHandler("file", cmd_file))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))

    print("✅ Atlas Telegram Bot Online!")
    print("🤖 Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    start_bot()