"""
Gateway Manager — Routes input to appropriate processor.
Text → Brain Pipeline
Voice → Voice Gateway → Brain
Image → Vision Gateway → Brain
"""

import os
from typing import Any, Dict, Optional

from core.interfaces.voice_gateway import VoiceGateway
from core.interfaces.vision_gateway import VisionGateway


class GatewayManager:
    """
    Central router for all input modalities.
    """

    def __init__(self):
        self._voice = VoiceGateway()
        self._vision = VisionGateway()

    def classify_input(self, input_data: Any) -> str:
        """
        Classify input type: text, voice, image, file.
        """
        if isinstance(input_data, str):
            return "text"
        
        if isinstance(input_data, dict):
            if input_data.get("type") == "voice":
                return "voice"
            if input_data.get("type") == "image":
                return "image"
            if input_data.get("type") == "file":
                return "file"
        
        # Check file extension
        if isinstance(input_data, str) and os.path.exists(input_data):
            ext = os.path.splitext(input_data)[1].lower()
            if ext in [".ogg", ".wav", ".mp3", ".m4a"]:
                return "voice"
            if ext in [".jpg", ".png", ".jpeg", ".gif", ".webp"]:
                return "image"
            if ext in [".pdf", ".docx", ".txt", ".py", ".json"]:
                return "file"
        
        return "text"

    def process(self, input_data: Any, query: str = None) -> Dict[str, Any]:
        """
        Process input through appropriate gateway.
        """
        input_type = self.classify_input(input_data)
        
        if input_type == "voice":
            transcript = self._voice.process_voice(input_data)
            return {"type": "voice", "transcript": transcript, "ready_for_brain": True}
        
        elif input_type == "image":
            description = self._vision.process_image(input_data, query)
            return {"type": "image", "description": description, "ready_for_brain": True}
        
        elif input_type == "file":
            return {"type": "file", "path": input_data, "ready_for_brain": True}
        
        else:
            return {"type": "text", "content": input_data, "ready_for_brain": True}
