import os
from openai import OpenAI

from core.personality import SYSTEM_PROMPT


class NvidiaProvider:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("NVIDIA_API_KEY"),
            base_url="https://integrate.api.nvidia.com/v1"
        )

        self.model = "meta/llama-3.3-70b-instruct"


    def chat(self, messages):

        # -------------------------
        # Atlas Personality
        # -------------------------

        final_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]


        final_messages.extend(messages)


        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=final_messages,
                temperature=0.5,
                max_tokens=512
            )


            return response.choices[0].message.content


        except Exception as e:

            return f"خطا در ارتباط با NVIDIA API: {e}"
