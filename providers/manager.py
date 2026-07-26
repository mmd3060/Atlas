import time

from providers.gemini import GeminiProvider
from providers.nvidia import NvidiaProvider
from providers.nrouter import NRouterProvider
from providers.github import GitHubProvider
from providers.openrouter import OpenRouterProvider


class ProviderManager:

    def __init__(self):

        self.providers = [

            GeminiProvider,
            NvidiaProvider,
            NRouterProvider,
            GitHubProvider,
            OpenRouterProvider,

        ]

        self.current_index = 0
        self._current_instance = None


    @property
    def current(self):

        if self._current_instance is None:

            self._current_instance = self.providers[
                self.current_index
            ]()

        return self._current_instance



    def current_name(self):

        return self.providers[
            self.current_index
        ].__name__.replace(
            "Provider",
            ""
        ).lower()



    def next_provider(self):

        old = self.current_name()


        self.current_index += 1


        if self.current_index >= len(self.providers):

            self.current_index = 0


        self._current_instance = None


        print(
            f"🔄 Switching: {old} → {self.current_name()}"
        )


        return self.current



    def reset(self):

        self.current_index = 0
        self._current_instance = None



    def set_provider(
        self,
        provider_name
    ):

        provider_name = provider_name.lower()


        aliases = {

            "google": "gemini",

            "gemini": "gemini",

            "nrouter": "nrouter",

            "nvidia": "nvidia",

            "github": "github",

            "openrouter": "openrouter",

        }


        provider_name = aliases.get(
            provider_name,
            provider_name
        )



        for index, provider in enumerate(self.providers):


            name = provider.__name__.replace(
                "Provider",
                ""
            ).lower()



            if name == provider_name:


                self.current_index = index

                self._current_instance = None


                return self.current



        raise ValueError(
            f"Unknown provider: {provider_name}"
        )



    def chat(
        self,
        messages
    ):

        attempts = len(
            self.providers
        )


        last_error = None



        for _ in range(attempts):


            provider = self.current_name()


            try:

                print(
                    f"🧠 Using: {provider}"
                )


                print(
                    f"📦 Messages: {len(messages)}"
                )


                start = time.time()


                answer = self.current.chat(
                    messages
                )


                elapsed = time.time() - start


                print(
                    f"⏱️ Response: {elapsed:.2f}s"
                )


                return answer



            except Exception as error:


                last_error = error


                print(
                    f"⚠️ {provider} failed: {error}"
                )


                self.next_provider()



        raise Exception(
            f"All providers failed: {last_error}"
        )
