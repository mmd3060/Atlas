from core.models.provider_resolver import ProviderResolver


resolver = ProviderResolver()


models = [

    "gemini-2.5-pro",
    "gpt-4.1",
    "qwen-coder"

]


for model in models:

    print()

    print(
        model
    )

    print(
        resolver.resolve(
            model
        )
    )
