"""
Vision Gateway — Processes image input.
"""

class VisionGateway:
    """
    Interfaces with vision services.
    
    Responsibilities:
      - Image analysis
      - OCR (text extraction from images)
      - Object detection
    """

    def process_image(self, image_path: str, query: str = None) -> str:
        """Analyze an image and return description."""
        return "[Image analysis: ...]"
