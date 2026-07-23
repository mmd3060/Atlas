from core.api_pool.pool_manager import APIPoolManager
from core.health.provider_health import ProviderHealthMonitor
from core.models.model_resolver import ModelResolver



class AtlasContainer:


    def __init__(self):

        # Shared API management

        self.api_pool = APIPoolManager()


        # Shared health system

        self.health = ProviderHealthMonitor()


        # Shared model intelligence

        self.models = ModelResolver()



    def register_provider(
        self,
        provider
    ):

        self.health.register_provider(
            provider
        )



    def add_api_key(
        self,
        provider,
        key
    ):

        self.api_pool.add_key(
            provider,
            key
        )



    def status(self):

        return {

            "api_pool": self.api_pool.show_status(),

            "providers": self.health.providers

        }
