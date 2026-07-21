import os
from openai import OpenAI


class GitHubProvider:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.github.ai/inference"
        )

        self.model = os.getenv(
            "MODEL_NAME",
            "meta/Llama-3.3-70B-Instruct"
        )

    def chat(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.8,
            max_tokens=2048
        )

        return response.choices[0].message.content
