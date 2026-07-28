"""
Voice Gateway — Speech-to-Text (STT) and Text-to-Speech (TTS).
Uses gTTS (free, no API key) for TTS and Whisper-compatible for STT.
"""

import os
import tempfile
from typing import Any, Dict, Optional

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class VoiceGateway:
    """
    Handles voice input/output for Atlas OS.
    
    STT: Convert voice message → text
    TTS: Convert text → voice message
    """

    def __init__(self):
        self._tts_lang = "fa"  # Default: Persian

    def text_to_speech(self, text: str, lang: str = None) -> Optional[str]:
        """
        Convert text to speech audio file.
        
        Returns:
            Path to .ogg file or None on error
        """
        lang = lang or self._tts_lang
        
        if not GTTS_AVAILABLE:
            # Fallback: use edge-tts if available
            return self._tts_edge(text, lang)
        
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            output_path = os.path.join(tempfile.gettempdir(), "atlas_voice.ogg")
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

    def _tts_edge(self, text: str, lang: str) -> Optional[str]:
        """Fallback TTS using edge-tts."""
        try:
            import asyncio
            import edge_tts
            
            output_path = os.path.join(tempfile.gettempdir(), "atlas_voice.ogg")
            
            async def _generate():
                voice = "fa-IR-DilaraNeural" if lang == "fa" else "en-US-GuyNeural"
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
            
            asyncio.run(_generate())
            return output_path
        except Exception:
            return None

    def speech_to_text(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Convert voice message to text.
        
        Telegram sends .ogg Opus files.
        We use a free API for transcription.
        """
        if not os.path.exists(audio_file_path):
            return {"error": "Audio file not found", "text": ""}
        
        if not REQUESTS_AVAILABLE:
            return {"error": "requests not installed", "text": ""}
        
        # Method 1: Try local whisper if available
        try:
            return self._whisper_local(audio_file_path)
        except Exception:
            pass
        
        # Method 2: Try free HuggingFace API
        try:
            return self._whisper_hf(audio_file_path)
        except Exception:
            pass
        
        return {
            "error": "STT engine not available. Install: pip install openai-whisper",
            "text": "",
            "suggestion": "Send your message as text instead.",
        }

    def _whisper_local(self, audio_path: str) -> Dict[str, Any]:
        """Use local Whisper model."""
        try:
            import whisper
            model = whisper.load_model("tiny")
            result = model.transcribe(audio_path)
            return {"text": result["text"], "language": result.get("language", "unknown")}
        except ImportError:
            raise Exception("whisper not installed")

    def _whisper_hf(self, audio_path: str) -> Dict[str, Any]:
        """Use HuggingFace Inference API for Whisper."""
        api_url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
        
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        response = requests.post(api_url, data=audio_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {"text": result.get("text", ""), "language": result.get("language", "unknown")}
        
        return {"error": f"API error: {response.status_code}", "text": ""}

    def detect_language(self, text: str) -> str:
        """Simple language detection."""
        persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        if persian_chars > len(text) * 0.3:
            return "fa"
        return "en"