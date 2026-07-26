import os

from openai import OpenAI

from core.personality import SYSTEM_PROMPT
from core.memory import get_memory_prompt
from memory.daily_memory import get_daily_prompt
from memory.chat_history import get_history, add_message


class GeminiProvider:


    def __init__(self):

        self.client = OpenAI(

            api_key=os.getenv(
                "GEMINI_API_KEY"
            ),

            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

        )


        self.model = os.getenv(

            "GEMINI_MODEL",

            "gemini-2.5-pro"

        )



    def chat(
        self,
        messages
    ):


        try:

            long_term_memory = get_memory_prompt()

        except Exception:

            long_term_memory = ""



        try:

            daily_memory = get_daily_prompt()

        except Exception:

            daily_memory = ""



        history = get_history()



        system_content = SYSTEM_PROMPT



        if long_term_memory:

            system_content += (

                "\n\nحافظه دائمی:\n"

                f"{long_term_memory}"

            )



        if daily_memory:

            system_content += (

                "\n\nوضعیت امروز:\n"

                f"{daily_memory}"

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
