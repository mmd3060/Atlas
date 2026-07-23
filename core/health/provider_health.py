class ProviderHealthMonitor:

    def __init__(self):
        self.providers = {}


    def register_provider(self, provider):

        self.providers[provider] = {
            "status": "healthy",
            "errors": 0,
            "last_error": None
        }


    def mark_error(self, provider, error):

        if provider not in self.providers:
            return

        self.providers[provider]["errors"] += 1
        self.providers[provider]["last_error"] = error


        if self.providers[provider]["errors"] >= 3:
            self.providers[provider]["status"] = "unhealthy"



    def set_status(self, provider, status):

        if provider in self.providers:
            self.providers[provider]["status"] = status



    def get_status(self, provider):

        if provider not in self.providers:
            return None

        return self.providers[provider]



    def show_all(self):

        return self.providers
