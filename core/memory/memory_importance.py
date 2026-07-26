class MemoryImportanceAnalyzer:
    """
    Memory Importance Analyzer v1.1

    تشخیص ارزش اطلاعات برای ذخیره در Memory System Atlas OS.
    """

    def __init__(self):

        self.ignore_patterns = [

            "سلام",

            "hello",

            "hi",

            "خوبی",

            "مرسی",

            "ممنون",

            "خداحافظ"

        ]


        self.rules = {


            "user": [

                "اسم من",

                "نام من",

                "من هستم",

                "علاقه دارم",

                "دوست دارم",

                "ترجیح میدم"

            ],



            "project": [

                "پروژه",

                "دارم می سازم",

                "در حال توسعه",

                "کد",

                "برنامه نویسی",

                "atlas os"

            ],



            "experience": [

                "خطا",

                "اشتباه",

                "مشکل",

                "حل شد",

                "راه حل"

            ]

        }




    def analyze(
        self,
        text
    ):


        original = text

        text = text.lower()



        # پیام‌های ساده

        for pattern in self.ignore_patterns:

            if pattern in text:

                return {

                    "text": original,

                    "importance": 0.1,

                    "category": "ignore",

                    "save": False

                }




        category = "short"

        importance = 0.2




        for memory_type, keywords in self.rules.items():

            for keyword in keywords:


                if keyword in text:


                    category = memory_type

                    importance = 0.8

                    break



            if category != "short":

                break




        # پروژه Atlas اهمیت بالا دارد

        if "atlas os" in text:

            category = "project"

            importance = 1.0




        return {

            "text": original,

            "importance": importance,

            "category": category,

            "save": importance >= 0.7

        }
