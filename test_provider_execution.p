from core.models.provider_resolver import ProviderResolver



resolver = ProviderResolver()



# ==========================
# Simulate API Pool
# ==========================

resolver.api_pool.add_key(
    "gemini",
    "GEMINI_KEY_1"
)


resolver.api_pool.add_key(
    "gemini",
    "GEMINI_KEY_2"
)


resolver.api_pool.add_key(
    "openrouter",
    "OPENROUTER_KEY_1"
)


resolver.api_pool.add_key(
    "github",
    "GITHUB_KEY_1"
)


resolver.api_pool.add_key(
    "nvidia",
    "NVIDIA_KEY_1"
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
# Pool Status
# ==========================

print("\n====================")

print(
    "API Pool Status:"
)


print(
    resolver.api_pool.show_status()
)
