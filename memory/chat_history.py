import json
import os

HISTORY_FILE = "memory/chat_history.json"
MAX_MESSAGES = 20


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history):
    history = history[-MAX_MESSAGES:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=4
        )


def add_message(role, content):

    # اگر متن None بود
    if content is None:
        return

    # تبدیل به رشته
    content = str(content).strip()

    # پیام خالی ذخیره نشود
    if content == "":
        return

    # پیام‌های خیلی بلند (معمولاً خروجی خراب مدل)
    if len(content) > 5000:
        return

    history = load_history()

    history.append({
        "role": role,
        "content": content
    })

    save_history(history)


def get_history():
    return load_history()


def clear_history():
    save_history([])
