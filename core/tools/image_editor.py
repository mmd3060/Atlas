"""
Vision Tools — Image processing capabilities for Atlas OS.

Supports:
  - FeyNoBg: Background removal (via HuggingFace API)
  - Image analysis (via Gemini Vision)
"""

import os
import base64
import requests
from typing import Any, Dict, Optional


class ImageEditor:
    """
    Image manipulation tools for Atlas OS.
    """

    HF_API_URL = "https://api-inference.huggingface.co/models/feyninc/FeyNobg"

    def __init__(self, hf_token: str = None):
        self._hf_token = hf_token or os.getenv("HUGGINGFACE_TOKEN", "")

    def remove_background(self, image_path: str, output_path: str = None) -> Dict[str, Any]:
        """
        Remove background from image using FeyNoBg model.

        Args:
            image_path: Path to input image
            output_path: Path to save result (defaults to input_nobg.png)

        Returns:
            {status, output_path} or {error}
        """
        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_path}"}

        if not output_path:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_nobg.png"

        try:
            # Read image
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Call HuggingFace API
            headers = {"Authorization": f"Bearer {self._hf_token}"} if self._hf_token else {}
            
            response = requests.post(
                self.HF_API_URL,
                headers=headers,
                data=image_data,
                timeout=60,
            )

            if response.status_code == 200:
                # Save result
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                return {
                    "status": "success",
                    "output_path": output_path,
                    "model": "FeyNoBg",
                }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "details": response.text[:200],
                }

        except requests.Timeout:
            return {"error": "Request timed out (60s)"}
        except Exception as e:
            return {"error": str(e)}

    def analyze_image(self, image_path: str, query: str = "Describe this image") -> Dict[str, Any]:
        """
        Analyze image content (placeholder for Gemini Vision integration).
        """
        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_path}"}

        return {
            "status": "success",
            "description": f"[Analysis of {image_path} with query: {query}]",
            "engine": "Gemini Vision (pending integration)",
        }