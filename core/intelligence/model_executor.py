import time

from providers.manager import ProviderManager
from core.models.model_registry import ModelRegistry


class ModelExecutor:


    def __init__(self):

        self.provider_manager = ProviderManager()

        self.registry = ModelRegistry()



    def execute(
        self,
        decision,
        messages
    ):


        model = decision.get(
            "model"
        )


        # گرفتن provider واقعی از Registry

        provider = self.registry.get_provider(
            model
        )


        result = {

            "model": model,

            "provider": provider,

            "status": "failed",

            "answer": None,

            "time": 0,

            "error": None

        }


        start = time.time()



        try:


            if not provider:

                raise Exception(
                    f"Unknown model: {model}"
                )



            self.provider_manager.set_provider(
                provider
            )



            print(
                f"🤖 Executing: {model}"
            )


            print(
                f"🧠 Using provider: {provider}"
            )



            answer = self.provider_manager.chat(
                messages
            )



            result["answer"] = answer

            result["status"] = "success"



        except Exception as error:


            result["error"] = str(error)


            print(
                f"❌ Execution failed: {error}"
            )



        finally:


            result["time"] = round(
                time.time() - start,
                2
            )



        return result
