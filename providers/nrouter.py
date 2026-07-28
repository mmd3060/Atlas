"""
NRouter Provider — Placeholder for NVIDIA Router.
"""

class NRouterProvider:
    """NVIDIA Router provider."""
    
    def __init__(self):
        self.name = "nrouter"
    
    def chat(self, messages):
        """Send messages to NRouter."""
        raise NotImplementedError("NRouter provider not configured")
    
    def set_api_key(self, key):
        pass
    
    def health_check(self):
        return {"status": "inactive"}