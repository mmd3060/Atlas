from core.models.provider_mapping import ProviderMapping
from core.models.model_resolver import ModelResolver

from core.container import AtlasContainer



class ProviderResolver:


    def __init__(
        self,
        container=None
    ):


        if container is None:

            container = AtlasContainer()



        self.container = container

        self.model_resolver = container.models

        self.health = container.health

        self.api_pool = container.api_pool




    def calculate_score(
        self,
        logical_provider,
        execution_provider,
        model
    ):


        score = 0



        # ==========================
        # Health Intelligence
        # ==========================

        health = self.health.get_status(
            execution_provider
        )



        if health is None:

            health = {
                "status": "healthy",
                "errors": 0
            }



        if health["status"] == "healthy":

            score += 10

        else:

            score -= 10




        # ==========================
        # Model Intelligence
        # ==========================

        score += model.get(
            "cost",
            5
        )


        score += (
            model.get(
                "context",
                5
            ) / 2
        )




        # ==========================
        # Provider Intelligence
        # ==========================

        provider_priority = {


            "gemini": 5,

            "openrouter": 4,

            "github": 4,

            "nvidia": 4


        }



        score += provider_priority.get(
            execution_provider,
            3
        )



        return round(
            score,
            2
        )





    def resolve(
        self,
        model_name
    ):


        # پیدا کردن مدل

        model = self.model_resolver.resolve(
            model_name
        )



        providers = model["providers"]



        best_logical_provider = None

        best_execution_provider = None

        best_score = -1




        for logical_provider in providers:



            execution_provider = ProviderMapping.resolve(
                logical_provider
            )



            score = self.calculate_score(
                logical_provider,
                execution_provider,
                model
            )



            if score > best_score:


                best_score = score

                best_logical_provider = logical_provider

                best_execution_provider = execution_provider





        # API Key

        api_key = self.api_pool.get_key(
            best_execution_provider
        )




        return {


            "model": model_name,


            "logical_provider": best_logical_provider,


            "execution_provider": best_execution_provider,


            "api_key": api_key,


            "score": best_score,


            "health": self.health.get_status(
                best_execution_provider
            )


        }
