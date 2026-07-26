from core.models.schemas import (
    ModelProfile,
    ModelCapabilities
)


class ModelRegistry:
    """
    Single Source of Truth for Atlas models.

    Atlas OS فقط مدل‌ها را می‌شناسد.
    Provider mapping در لایه جدا مدیریت می‌شود.
    """

    def __init__(self):

        self.models = {

            "gpt-4.1": ModelProfile(

                name="gpt-4.1",

                capabilities=ModelCapabilities(

                    coding=10,
                    math=9,
                    text=9,
                    vision=8,
                    reasoning=10,
                    multilingual=8,

                ),

                context_window=128000,

                speed=0.85,

                cost=0.35,

                providers=[
                    "github",
                    "openrouter"
                ],

                tags=[
                    "coding",
                    "reasoning",
                    "general"
                ]

            ),


            "gemini-2.5-pro": ModelProfile(

                name="gemini-2.5-pro",

                capabilities=ModelCapabilities(

                    coding=8,
                    math=10,
                    text=9,
                    vision=10,
                    reasoning=10,
                    multilingual=10,

                ),

                context_window=1000000,

                speed=0.8,

                cost=0.7,

                providers=[
                    "gemini",
                    "openrouter"
                ],

                tags=[
                    "math",
                    "vision",
                    "reasoning"
                ]

            ),



            "llama-3.3-70b": ModelProfile(

                name="llama-3.3-70b",

                capabilities=ModelCapabilities(

                    coding=9,
                    math=8,
                    text=8,
                    vision=5,
                    reasoning=8,
                    multilingual=7,

                ),

                context_window=131072,

                speed=0.9,

                cost=0.95,

                providers=[
                    "nvidia",
                    "openrouter"
                ],

                tags=[
                    "fast",
                    "cheap",
                    "coding"
                ]

            ),


            "qwen-coder": ModelProfile(

                name="qwen-coder",

                capabilities=ModelCapabilities(

                    coding=10,
                    math=8,
                    text=7,
                    vision=5,
                    reasoning=8,
                    multilingual=8,

                ),

                context_window=32768,

                speed=0.85,

                cost=0.9,

                providers=[
                    "openrouter",
                    "nvidia"
                ],

                tags=[
                    "coding"
                ]

            ),

        }



    def get_model(self, name):

        return self.models.get(name)



    def get_all(self):

        return list(
            self.models.values()
        )



    def list_models(self):

        return {

            name: model.to_dict()

            for name, model in self.models.items()

        }



    def has_model(self, name):

        return name in self.models
