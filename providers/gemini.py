import os

from openai import OpenAI

from core.personality import SYSTEM_PROMPT
from memory.daily_memory import get_daily_prompt
from memory.chat_history import get_history, add_message


def get_memory_prompt():

    try:
        from core.memory.context_builder import ContextBuilder

        builder = ContextBuilder()
        context = builder.build()

        if not context:
            return ""

        return str(context)

    except Exception:
        return ""



class GeminiProvider:


    def __init__(self):

        self.client = OpenAI(

            api_key=os.getenv(
                "GEMINI_KEY_1"
            ),

            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

        )


        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-pro"
        )



    def chat(self, messages):

        memory = get_memory_prompt()


        try:
            daily = get_daily_prompt()
        except Exception:
            daily = ""


        history = get_history()


        system_content = SYSTEM_PROMPT


        if memory:
            system_content += (
                "\n\nMemory Context:\n"
                + memory
            )


        if daily:
            system_content += (
                "\n\nDaily Context:\n"
                + daily
            )


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

            temperature=0.7,

            max_tokens=2048

        )


        answer = response.choices[0].message.content


        for msg in messages:
            add_message(
                msg["role"],
                msg["content"]
            )


        add_message(
            "assistant",
            answer
        )


        return answer
