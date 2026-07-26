from core.intelligence.task_analyzer import TaskAnalyzer


analyzer = TaskAnalyzer()


tests = [

    "سلام حالت چطوره",

    "write python api for telegram bot",

    "قیمت بیت کوین الان چنده",

    "حل کن این معادله را"

]


for text in tests:

    print("\n================")

    print(text)

    print(
        analyzer.analyze(text)
    )
