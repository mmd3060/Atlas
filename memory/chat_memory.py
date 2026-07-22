import json
import os

MEMORY_FILE = "memory/chat_history.json"


def load_chat():
    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chat(messages):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)


def add_message(role, content):
    messages = load_chat()

    messages.append({
        "role": role,
        "content": content
    })

    # فقط آخرین 20 پیام را نگه می‌داریم
    messages = messages[-8:]

    save_chat(messages)

    return messages
