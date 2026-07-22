import json
import os

USERS_DIR = "memory/users"

os.makedirs(USERS_DIR, exist_ok=True)


def _user_file(user_id: int | str):
    return os.path.join(
        USERS_DIR,
        f"{user_id}.json"
    )


def load_chat(user_id):

    file_path = _user_file(user_id)

    if not os.path.exists(file_path):
        return []

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return []


def save_chat(user_id, messages):

    file_path = _user_file(user_id)

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            messages,
            f,
            ensure_ascii=False,
            indent=4
        )


def add_message(
    user_id,
    role,
    content
):

    messages = load_chat(user_id)

    messages.append({

        "role": role,

        "content": content

    })

    # فقط آخرین 8 پیام
    messages = messages[-8:]

    save_chat(
        user_id,
        messages
    )

    return messages


def clear_chat(user_id):

    save_chat(
        user_id,
        []
    )
