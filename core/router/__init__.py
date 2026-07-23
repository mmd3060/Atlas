from .smart_router import SmartRouter
from providers.manager import ProviderManager


# Router اصلی Atlas
router = SmartRouter()


def get_provider(message):
    """
    Smart Router
        ↓
    انتخاب Provider
        ↓
    برگرداندن ProviderManager
    (برای سازگاری با interface فعلی)
    """

    decision = router.route(message)

    provider_name = decision["provider"]

    manager = ProviderManager()

    manager.set_provider(provider_name)

    return manager
