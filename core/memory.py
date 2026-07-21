import json
import os

MEMORY_FILE = "memory/long_term.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_memory_prompt():
    memory = load_memory()

    if not memory:
        return ""

    text = "اطلاعاتی که درباره محمد می‌دانی:\n"

    for key, value in memory.items():
        text += f"- {key}: {value}\n"

    return text
