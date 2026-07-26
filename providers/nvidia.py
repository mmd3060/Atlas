import os

from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

from core.personality import SYSTEM_PROMPT


class NvidiaProvider:

    def __init__(self):

        self.keys = [
            os.getenv("NVIDIA_KEY_1"),
            os.getenv("NVIDIA_KEY_2"),
            os.getenv("NVIDIA_KEY_3"),
        ]

        self.keys = [
            key for key in self.keys
            if key
        ]

        if not self.keys:
            raise RuntimeError(
                "No NVIDIA API keys configured"
            )

        self.current_key = 0

        self.model = os.getenv(
            "NVIDIA_MODEL",
            "meta/llama-3.3-70b-instruct"
        )


    def _client(self):

        return OpenAI(
            api_key=self.keys[self.current_key],
            base_url="https://integrate.api.nvidia.com/v1"
        )


    def _switch_key(self):

        if len(self.keys) <= 1:
            return False

        self.current_key += 1

        if self.current_key >= len(self.keys):
            self.current_key = 0

        print(
            f"🔑 NVIDIA key switched -> {self.current_key + 1}"
        )

        return True


    def chat(self, messages):

        final_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        final_messages.extend(messages)


        attempts = len(self.keys)


        last_error = None


        for _ in range(attempts):

            try:

                print(
                    f"🟢 NVIDIA using key {self.current_key + 1}"
                )


                response = self._client().chat.completions.create(

                    model=self.model,

                    messages=final_messages,

                    temperature=0.5,

                    max_tokens=1024

                )


                return response.choices[0].message.content


            except Exception as e:

                last_error = e

                print(
                    f"⚠️ NVIDIA key failed: {e}"
                )

                self._switch_key()


        raise Exception(
            f"NVIDIA all keys failed: {last_error}"
        )
