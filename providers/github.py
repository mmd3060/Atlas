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


        long_term_memory = get_memory_prompt()


        try:
            daily_memory = get_daily_prompt()

        except Exception:
            daily_memory = ""



        history = get_history()



        system_content = SYSTEM_PROMPT



        if long_term_memory:

            system_content += (
                "\n\nMemory Context:\n"
                + long_term_memory
            )



        if daily_memory:

            system_content += (
                "\n\nDaily Context:\n"
                + daily_memory
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

            temperature=0.8,

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
