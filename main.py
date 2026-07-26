import time
import os

from dotenv import load_dotenv

from core.router import get_provider
from memory.chat_memory import add_message
from stats.token_tracker import get_usage_report
from providers.manager import ProviderManager


# Load environment variables
load_dotenv()


# =========================
# Provider System
# =========================

ai = get_provider()

manager = ProviderManager()


# اگر Router یک Provider مشخص داده باشد
if isinstance(ai, dict):

    provider_name = ai.get(
        "provider",
        "gemini"
    )

    try:
        manager.set_provider(
            provider_name
        )
    except ValueError:
        manager.reset()


print("Atlas آنلاین شد 🚀")


print(
    f"Provider: {manager.current_name()}"
)


print(
    "برای خروج بنویس: exit"
)


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



    # Token Usage

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



    # Provider Switch

    if command.startswith(
        "/provider"
    ):

        parts = user_input.split()


        if len(parts) < 2:

            print(
                "Atlas: نام Provider را وارد کن."
            )

            continue


        provider_name = parts[1]


        try:

            manager.set_provider(
                provider_name
            )


            print(
                f"✅ Provider changed to: {manager.current_name()}"
            )


        except Exception as error:

            print(
                f"⚠️ Provider Error: {error}"
            )


        continue



    # Current Provider Status

    if command == "/status":

        print(
            f"🧠 Current Provider: {manager.current_name()}"
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


        answer = manager.chat(
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
