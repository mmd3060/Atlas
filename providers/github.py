import os
from openai import OpenAI

from core.personality import SYSTEM_PROMPT
from core.memory import get_memory_prompt
from memory.daily_memory import get_daily_prompt
from memory.chat_history import get_history, add_message

class GitHubProvider:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.github.ai/inference"
        )

        self.model = os.getenv(
            "GITHUB_MODEL",
            "openai/gpt-4.1"
        )


    def chat(self, messages):

        # -------------------------
        # Memory System
        # -------------------------

        try:
            long_term_memory = get_memory_prompt()
        except Exception:
            long_term_memory = ""


        try:
            daily_memory = get_daily_prompt()
        except Exception:
            daily_memory = ""


        # حافظه کوتاه‌مدت مکالمه
        history = get_history()


        # -------------------------
        # Atlas Personality
        # -------------------------

        system_content = SYSTEM_PROMPT


        # حافظه دائمی محمد
        if long_term_memory:

            system_content += (
                "\n\n"
                "حافظه دائمی درباره محمد:\n"
                f"{long_term_memory}"
            )


        # حال و هوای امروز
        if daily_memory:

            system_content += (
                "\n\n"
                "وضعیت موقت امروز محمد:\n"
                f"{daily_memory}"
            )


        # -------------------------
        # Send to Model
        # -------------------------

        final_messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]



        final_messages.extend(history)

        final_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=final_messages,
            temperature=0.8,
            max_tokens=2048
        )

        answer = response.choices[0].message.content

        # ذخیره پیام‌های جدید در حافظه کوتاه‌مدت
        for msg in messages:
            add_message(msg["role"], msg["content"])

        add_message("assistant", answer)

        return answer
