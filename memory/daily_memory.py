import json
import os
from datetime import datetime


MEMORY_FILE = "memory/daily_memory.json"


def load_daily_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_daily_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def add_daily_memory(key, value):
    memory = load_daily_memory()

    today = datetime.now().strftime("%Y-%m-%d")

    if memory.get("date") != today:
        memory = {
            "date": today,
            "notes": []
        }

    memory["notes"].append({
        "key": key,
        "value": value
    })

    save_daily_memory(memory)


def get_daily_prompt():
    memory = load_daily_memory()

    if not memory:
        return ""

    text = "اطلاعات موقت امروز محمد:\n"

    for item in memory.get("notes", []):
        text += f"- {item['key']}: {item['value']}\n"

    return text
