from core.intelligence.intelligence_engine import IntelligenceEngine



engine = IntelligenceEngine()



tests = [

    "write python api for telegram bot",

    "حل کن این معادله را",

    "قیمت بیت کوین الان چنده",

    "سلام حالت چطوره"

]



for text in tests:


    print("\n================")

    print(text)


    result = engine.analyze(
        text
    )


    print(result)
