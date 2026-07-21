import os
from dotenv import load_dotenv
from core.router import get_provider

load_dotenv()

ai = get_provider()

messages = [
    {
        "role": "user",
        "content": "سلام Atlas، خودت را معرفی کن."
    }
]

answer = ai.chat(messages)

print(answer)
