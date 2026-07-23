class ProviderMapping:


    mapping = {

        "google": "gemini",

        "github": "github",

        "nvidia": "nvidia",

        "openrouter": "openrouter"

    }



    @classmethod
    def resolve(cls, provider):

        return cls.mapping.get(
            provider,
            provider
        )
