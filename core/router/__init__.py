from .smart_router import SmartRouter
from providers.manager import ProviderManager


router = SmartRouter()


def get_provider(message):

    decision = router.route(message)

    provider_name = decision.get(
        "execution_provider"
    )

    if provider_name is None:

        provider_name = decision.get(
            "provider"
        )

    manager = ProviderManager()

    manager.set_provider(
        provider_name
    )

    return manager
