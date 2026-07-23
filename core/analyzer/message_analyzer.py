class MessageAnalyzer:

    def analyze(self, message):

        result = {
            "type": "text",
            "complexity": "normal",
            "needs_vision": False,
            "needs_voice": False
        }


        # تشخیص کد
        code_keywords = [
            "python",
            "java",
            "javascript",
            "code",
            "function",
            "class",
            "import"
        ]

        if any(word in message.lower() for word in code_keywords):
            result["type"] = "code"


        # تشخیص ریاضی
        math_symbols = [
            "+",
            "-",
            "*",
            "/",
            "=",
            "√"
        ]

        if any(symbol in message for symbol in math_symbols):
            result["type"] = "math"


        return result
