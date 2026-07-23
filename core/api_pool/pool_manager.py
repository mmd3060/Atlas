class APIPoolManager:

    def __init__(self):
        self.providers = {}


    def add_key(self, provider, key):

        if provider not in self.providers:
            self.providers[provider] = []

        self.providers[provider].append({
            "key": key,
            "status": "active",
            "usage": 0
        })


    def get_key(self, provider):

        if provider not in self.providers:
            return None


        active_keys = [
            item for item in self.providers[provider]
            if item["status"] == "active"
        ]


        if not active_keys:
            return None


        selected = min(
            active_keys,
            key=lambda x: x["usage"]
        )


        selected["usage"] += 1

        return selected["key"]



    def mark_failed(self, provider, key):

        if provider not in self.providers:
            return


        for item in self.providers[provider]:

            if item["key"] == key:
                item["status"] = "failed"



    def show_status(self):

        return self.providers
