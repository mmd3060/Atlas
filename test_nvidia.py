import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
)

try:
    models = client.models.list()

    print("Models available:")
    for model in models.data:
        print(model.id)

except Exception as e:
    print(e)
