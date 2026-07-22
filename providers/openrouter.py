import os

from openai import OpenAI

from core.personality import SYSTEM_PROMPT
from memory.chat_history import get_history
from stats.token_tracker import track_usage


class OpenRouterProvider:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv(
                "OPENROUTER_API_KEY"
            ),
            base_url="https://openrouter.ai/api/v1"
        )

        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "qwen/qwen2.5-7b-instruct:free"
        )


    def chat(self, messages):

        history = get_history()


        final_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]


        final_messages.extend(history)
        final_messages.extend(messages)


        response = self.client.chat.completions.create(
            model=self.model,
            messages=final_messages,
            temperature=0.8,
            max_tokens=512
        )


        # ثبت مصرف توکن‌ها
        if response.usage:

            track_usage(
                provider="OpenRouter",
                model=self.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens
            )


        return response.choices[0].message.content
