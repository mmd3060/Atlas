"""
Input Analyzer — Analyzes user input for task type, language, complexity.

Usage:
    analyzer = InputAnalyzer()
    result = analyzer.analyze("کد Python بنویس")
    # {task_type, language, complexity, keywords}
"""

from typing import Any, Dict, List


class InputAnalyzer:
    """
    Analyzes user input to determine task characteristics.
    """

    def analyze(self, message: str) -> Dict[str, Any]:
        """
        Analyze a user message.

        Returns:
            {task_type, language, complexity, keywords}
        """
        msg_lower = message.lower()

        # ── Task type detection ──
        task_type = "general"
        if any(w in msg_lower for w in ["کد", "code", "program", "python", "def ", "class ", "function"]):
            task_type = "coding"
        elif any(w in msg_lower for w in ["ریاضی", "math", "calculate", "محاسبه", "formula"]):
            task_type = "math"
        elif any(w in msg_lower for w in ["ترجمه", "translate", "توضیح", "explain", "تعریف"]):
            task_type = "text"
        elif any(w in msg_lower for w in ["تحلیل", "analyze", "بررسی", "review"]):
            task_type = "analysis"
        elif any(w in msg_lower for w in ["ادامه", "continue", "next", "مرحله"]):
            task_type = "continuation"

        # ── Language detection ──
        language = "en"
        persian_chars = sum(1 for c in message if '\u0600' <= c <= '\u06FF')
        if persian_chars > len(message) * 0.2:
            language = "fa"

        # ── Complexity detection ──
        complexity = "medium"
        if len(message) < 20:
            complexity = "low"
        elif len(message) > 100 or any(w in msg_lower for w in ["پیچیده", "complex", "advanced", "deep"]):
            complexity = "high"

        # ── Keywords ──
        keywords = [w for w in message.split() if len(w) > 3][:5]

        return {
            "task_type": task_type,
            "language": language,
            "complexity": complexity,
            "keywords": keywords,
            "message_length": len(message),
        }
