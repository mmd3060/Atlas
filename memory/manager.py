import json
import os
from datetime import datetime


DAILY_FILE = "memory/daily.json"
ARCHIVE_DIR = "memory/archive"


def load_daily():
    if not os.path.exists(DAILY_FILE):
        return {}

    with open(DAILY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_daily(data):
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def add_daily(key, value):
    data = load_daily()

    data[key] = value

    save_daily(data)


def get_daily_prompt():
    data = load_daily()

    if not data:
        return ""

    text = "اطلاعات موقت امروز محمد:\n"

    for key, value in data.items():
        text += f"- {key}: {value}\n"

    return text


def archive_daily():

    data = load_daily()

    if not data:
        return

    date = datetime.now().strftime("%Y-%m-%d")

    path = f"{ARCHIVE_DIR}/{date}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

    save_daily({})
