import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference"
)

response = client.chat.completions.create(
    model="meta/Llama-3.3-70B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "سلام، فقط بگو OK"
        }
    ],
    temperature=0.8,
    max_tokens=100
)

print(response.choices[0].message.content)
