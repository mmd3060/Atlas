class FallbackManager:

    def __init__(self):

        self.routes = {

            "code": [
                "github",
                "gemini",
                "openrouter",
                "nvidia"
            ],


            "math": [
                "gemini",
                "openrouter"
            ],


            "text": [
                "gemini",
                "openrouter"
            ]

        }



    def get_fallback_chain(self, task_type):

        return self.routes.get(
            task_type,
            ["gemini"]
        )



    def choose_provider(self, task_type, health_monitor):

        providers = self.get_fallback_chain(task_type)


        for provider in providers:

            status = health_monitor.get_status(provider)


            if status is None:
                continue


            if status["status"] == "healthy":

                return provider


        return None
