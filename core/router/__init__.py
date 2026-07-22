import os

from providers.manager import ProviderManager
from core.smart_router import detect_task, choose_provider


_manager = ProviderManager()


def get_provider(message=None):

    if message:

        task = detect_task(message)

        provider = choose_provider(task)

        print(
            f"🧠 Smart Router: {task.category}"
        )

        print(
            f"🎯 Selected Provider: {provider}"
        )

        try:
            _manager.set_provider(provider)

        except ValueError:
            print(
                f"⚠️ Provider {provider} not found"
            )


    else:

        provider = os.getenv(
            "DEFAULT_PROVIDER",
            ""
        ).lower()


        if provider:

            try:
                _manager.set_provider(provider)

            except ValueError:
                pass


    return _manager
