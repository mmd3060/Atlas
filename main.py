import os

from dotenv import load_dotenv

from core.router import get_provider
from memory.chat_memory import add_message


# Load environment variables
load_dotenv()


# Start AI provider
ai = get_provider()


print("Atlas آنلاین شد 🚀")
print(
    f"Provider: {ai.current_name()}"
)
print("برای خروج بنویس: exit")


while True:

    user_input = input("\nمحمد: ").strip()


    if not user_input:
        print("Atlas: یک پیام بنویس محمد 🙂")
        continue


    if user_input.lower() == "exit":

        print(
            "Atlas: فعلاً خداحافظ محمد 🦔⚡"
        )

        break


    try:

        # Save user message
        messages = add_message(
            "user",
            user_input
        )


        # Get response
        answer = ai.chat(
            messages
        )


        print(
            "\nAtlas:",
            answer
        )


        # Save Atlas response
        add_message(
            "assistant",
            answer
        )


    except Exception as error:

        print(
            "\n⚠️ Atlas Error:",
            error
        )
