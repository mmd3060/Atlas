class TokenAnalyzer:


    def __init__(self):

        self.large_keywords = [

            "مقاله",
            "کامل",
            "جزئیات",
            "تحلیل",
            "بررسی عمیق",
            "تحقیق",
            "توضیح جامع",
            "راهنما"

        ]


        self.code_keywords = [

            "کد",
            "python",
            "برنامه",
            "debug",
            "خطا",
            "باگ"

        ]



    def estimate_tokens(self, text):

        words = len(text.split())

        return int(words * 1.3)



    def detect_intent(self, text):


        text = text.lower()


        for word in self.code_keywords:

            if word in text:

                return "coding"



        for word in self.large_keywords:

            if word in text:

                return "long_generation"



        return "normal"



    def estimate_complexity(self, text, tokens, intent):


        if intent == "long_generation":

            return "large"


        if intent == "coding":

            return "medium"



        if tokens < 50:

            return "small"



        elif tokens < 500:

            return "medium"


        else:

            return "large"



    def analyze(self, text):


        tokens = self.estimate_tokens(text)


        intent = self.detect_intent(text)


        complexity = self.estimate_complexity(
            text,
            tokens,
            intent
        )



        return {

            "tokens": tokens,

            "intent": intent,

            "complexity": complexity

        }
