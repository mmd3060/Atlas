"""
Task Classifier — Classifies input tasks for routing.

Usage:
    classifier = TaskClassifier()
    result = classifier.classify("این کد پایتون چرا خطا میده؟")
    # {type, complexity, needs_reasoning, needs_tools, language}
"""

from typing import Any, Dict


class TaskClassifier:
    """
    Classifies user input into task types.
    """

    def classify(self, message: str) -> Dict[str, Any]:
        """
        Classify a user message.

        Returns:
            {type, complexity, needs_reasoning, needs_tools, language}
        """
        msg_lower = message.lower()

        # ── Task type ──
        task_type = "general"
        if any(w in msg_lower for w in ["کد", "code", "program", "python", "def ", "class ", "function", "error", "debug", "خطا", "باگ"]):
            task_type = "code"
        elif any(w in msg_lower for w in ["ریاضی", "math", "calculate", "محاسبه", "integral", "انتگرال", "معادله"]):
            task_type = "math"
        elif any(w in msg_lower for w in ["ترجمه", "translate", "توضیح", "explain", "نوشتن", "write", "مقاله"]):
            task_type = "text"
        elif any(w in msg_lower for w in ["تحلیل", "analyze", "بررسی", "review", "compares"]):
            task_type = "analysis"
        elif any(w in msg_lower for w in ["عکس", "image", "تصویر", " screenshot", "photo"]):
            task_type = "vision"
        elif any(w in msg_lower for w in ["ویس", "voice", "صدا", "صحبت"]):
            task_type = "voice"

        # ── Complexity ──
        complexity = "medium"
        if len(message) < 20:
            complexity = "low"
        elif len(message) > 100 or any(w in msg_lower for w in ["پیچیده", "complex", "advanced", "deep", "سخت"]):
            complexity = "high"

        # ── Needs reasoning ──
        needs_reasoning = task_type in ("code", "math", "analysis") or complexity == "high"

        # ── Needs tools ──
        needs_tools = any(w in msg_lower for w in ["اجرا", "run", "فایل", "file", "terminal", "git", "search"])

        # ── Language ──
        persian_chars = sum(1 for c in message if '\u0600' <= c <= '\u06FF')
        language = "fa" if persian_chars > len(message) * 0.2 else "en"

        return {
            "type": task_type,
            "complexity": complexity,
            "needs_reasoning": needs_reasoning,
            "needs_tools": needs_tools,
            "language": language,
            "message_length": len(message),
        }
