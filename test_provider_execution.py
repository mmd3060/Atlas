from core.container import AtlasContainer
from core.models.provider_resolver import ProviderResolver



# ==========================
# Create Atlas Core Container
# ==========================

container = AtlasContainer()



# ==========================
# Register Providers
# ==========================

providers = [

    "gemini",
    "github",
    "nvidia",
    "openrouter"

]


for provider in providers:

    container.register_provider(
        provider
    )



# ==========================
# Add API Keys
# ==========================

container.add_api_key(
    "gemini",
    "GEMINI_KEY_1"
)


container.add_api_key(
    "gemini",
    "GEMINI_KEY_2"
)


container.add_api_key(
    "openrouter",
    "OPENROUTER_KEY_1"
)


container.add_api_key(
    "github",
    "GITHUB_KEY_1"
)


container.add_api_key(
    "nvidia",
    "NVIDIA_KEY_1"
)




# ==========================
# Create Resolver
# ==========================

resolver = ProviderResolver(
    container
)




# ==========================
# Models To Test
# ==========================

tests = [

    "gemini-2.5-pro",

    "gpt-4.1",

    "qwen-coder"

]




# ==========================
# Resolver Test
# ==========================

for model in tests:


    print("\n====================")

    print(
        "Testing Model:",
        model
    )


    result = resolver.resolve(
        model
    )


    print(
        result
    )





# ==========================
# Container Status
# ==========================

print("\n====================")

print(
    "Atlas Container Status:"
)


print(
    container.status()
)
