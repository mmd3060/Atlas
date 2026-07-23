from core.models.provider_mapping import ProviderMapping


tests = [

    "google",
    "github",
    "nvidia",
    "openrouter",
    "unknown"

]


for provider in tests:

    print(
        provider,
        "=>",
        ProviderMapping.resolve(provider)
    )
