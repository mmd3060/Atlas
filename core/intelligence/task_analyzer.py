class TaskAnalyzer:


    def analyze(self, message):

        text = message.lower()

        words = text.split()


        task_type = "text"

        difficulty = "normal"


        # =========================
        # Code Detection
        # =========================

        code_keywords = [
            "python",
            "code",
            "program",
            "bug",
            "error",
            "function",
            "class",
            "api",
            "script",
            "algorithm",
            "کد",
            "برنامه"
        ]


        if any(word in text for word in code_keywords):

            task_type = "code"



        # =========================
        # Math Detection
        # =========================

        math_keywords = [
            "calculate",
            "equation",
            "solve",
            "formula",
            "math",
            "ریاضی",
            "معادله",
            "حل کن"
        ]


        if any(word in text for word in math_keywords):

            task_type = "math"



        # =========================
        # Reasoning / Architecture
        # =========================

        reasoning_keywords = [
            "design",
            "architecture",
            "system",
            "agent",
            "strategy",
            "analyze",
            "compare",
            "طراحی",
            "معماری",
            "سیستم",
            "تحلیل",
            "مقایسه"
        ]


        if any(word in text for word in reasoning_keywords):

            task_type = "reasoning"



        # =========================
        # Research / Information
        # =========================

        research_keywords = [
            "research",
            "explain",
            "history",
            "information",
            "بررسی",
            "توضیح",
            "اطلاعات"
        ]


        if any(word in text for word in research_keywords):

            task_type = "research"



        # =========================
        # Tool Detection
        # =========================

        tool_keywords = [
            "price",
            "bitcoin",
            "weather",
            "search",
            "news",
            "قیمت",
            "بیت",
            "هوا",
            "جستجو",
            "خبر"
        ]


        requires_tool = any(
            word in text
            for word in tool_keywords
        )



        # =========================
        # Difficulty Intelligence
        # =========================


        high_complexity_keywords = [
            "architecture",
            "agent",
            "system",
            "design",
            "strategy",
            "advanced",
            "پیچیده",
            "معماری",
            "طراحی",
            "سیستم",
            "پروژه"
        ]


        if any(
            word in text
            for word in high_complexity_keywords
        ):

            difficulty = "high"


        elif len(words) < 5:

            difficulty = "low"


        elif len(words) > 50:

            difficulty = "high"



        return {

            "type": task_type,

            "difficulty": difficulty,

            "requires_tool": requires_tool,

            "length": len(words)

        }
