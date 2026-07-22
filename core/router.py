import os

from providers.manager import ProviderManager


_manager = ProviderManager()


def get_provider():

    provider = os.getenv(
        "DEFAULT_PROVIDER",
        ""
    ).lower()


    if provider:

        _manager.set_provider(
            provider
        )


    return _manager
