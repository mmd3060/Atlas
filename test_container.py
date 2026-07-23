from core.container import AtlasContainer



atlas = AtlasContainer()



atlas.register_provider(
    "gemini"
)


atlas.register_provider(
    "github"
)


atlas.add_api_key(
    "gemini",
    "GEMINI_KEY_1"
)


atlas.add_api_key(
    "github",
    "GITHUB_KEY_1"
)



print(
    atlas.status()
)
