import time
import os

from dotenv import load_dotenv

from core.router import get_provider
from memory.chat_memory import add_message
from stats.token_tracker import get_usage_report


# Load environment variables
load_dotenv()


# Start AI provider
ai = get_provider()


print("Atlas آنلاین شد 🚀")
if isinstance(ai, dict):
    print(f"Provider: {ai.get('provider', 'unknown')}")
else:
    print(f"Provider: {ai.current_name()}")
print("برای خروج بنویس: exit")


while True:

    user_input = input("\nمحمد: ").strip()


    if not user_input:
        print(
            "Atlas: یک پیام بنویس محمد 🙂"
        )
        continue


    if user_input.lower() == "exit":

        print(
            "Atlas: فعلاً خداحافظ محمد 🦔⚡"
        )

        break



    # =========================
    # Atlas Commands
    # =========================

    command = user_input.lower()


    if command in [
        "وضعیت مصرف",
        "مصرف توکن",
        "token usage",
        "usage"
    ]:

        print(
            "\nAtlas:\n",
            get_usage_report()
        )

        continue



    # =========================
    # Normal AI Chat
    # =========================

    try:

        start = time.time()


        messages = add_message(
            "user",
            user_input
        )


        print(
            f"📦 Messages: {len(messages)}"
        )


        if isinstance(ai, dict):
            # Smart Router dict → resolve to real ProviderManager
            from providers.manager import ProviderManager
            provider_name = ai.get("provider", "gemini")
            manager = ProviderManager()
            try:
                manager.set_provider(provider_name)
            except ValueError:
                manager.reset()
            answer = manager.chat(messages)
        else:
            answer = ai.chat(
                messages
            )


        elapsed = time.time() - start


        print(
            f"⏱️ Response: {elapsed:.2f}s"
        )


        print(
            "\nAtlas:",
            answer
        )


        add_message(
            "assistant",
            answer
        )


    except Exception as error:

        print(
            "\n⚠️ Atlas Error:",
            error
        )
