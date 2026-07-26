from core.memory.memory_importance import MemoryImportanceAnalyzer
from core.memory.memory_engine import MemoryEngine


class MemoryPipeline:
    """
    Memory Pipeline v2.1

    لایه تصمیم گیری حافظه Atlas OS.

    وظایف:

    - تحلیل اهمیت پیام
    - تشخیص نوع حافظه
    - تصمیم ذخیره یا رد
    - ذخیره در MemoryEngine مرکزی
    - آماده برای Long Term Memory
    """


    def __init__(
        self,
        memory_engine=None
    ):

        self.analyzer = MemoryImportanceAnalyzer()


        # اگر از بیرون حافظه داده شد
        # از همان استفاده کن

        if memory_engine:

            self.memory = memory_engine


        else:

            # سازگاری با نسخه‌های قدیمی

            self.memory = MemoryEngine()



    def process(
        self,
        text
    ):

        analysis = self.analyzer.analyze(
            text
        )


        # اطلاعات بی‌اهمیت

        if not analysis["save"]:

            return {

                "status": "ignored",

                "analysis": analysis

            }



        category = analysis["category"]


        key = self.generate_key(
            text,
            category
        )


        self.memory.save(

            category,

            key,

            text

        )


        return {

            "status": "saved",

            "category": category,

            "key": key,

            "analysis": analysis

        }



    def generate_key(
        self,
        text,
        category=None
    ):


        words = text.split()


        # کلید بهتر برای حافظه

        if len(words) >= 3:

            key = "_".join(
                words[:3]
            )


        elif len(words) > 0:

            key = words[0]


        else:

            key = "empty"



        return key



    def get_memory_context(
        self
    ):

        return self.memory.get_context()
