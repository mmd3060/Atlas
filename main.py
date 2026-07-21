import os
from dotenv import load_dotenv
from core.router import get_provider
from memory.chat_memory import load_chat, add_message

load_dotenv()

ai = get_provider()

print("Atlas آنلاین شد 🚀")
print("برای خروج بنویس: exit")

# بارگذاری تاریخچه قبلی گفتگو
chat_history = load_chat()

while True:
    user_input = input("\nمحمد: ")

    if user_input.lower() == "exit":
        print("Atlas: فعلاً خداحافظ محمد 🦔⚡")
        break

    # اضافه کردن پیام محمد به حافظه
    messages = add_message(
        "user",
        user_input
    )

    answer = ai.chat(messages)

    print("\nAtlas:", answer)

    # ذخیره جواب Atlas در حافظه
    add_message(
        "assistant",
        answer
    )
