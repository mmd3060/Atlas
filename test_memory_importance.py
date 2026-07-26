from core.memory.memory_importance import MemoryImportanceAnalyzer


analyzer = MemoryImportanceAnalyzer()



tests = [

    "سلام Atlas",

    "اسم من محمد است",

    "من دارم پروژه Atlas OS را می سازم",

    "این خطا قبلا مشکل ایجاد کرده بود"

]


for t in tests:

    print("\nINPUT:")
    print(t)

    print(
        analyzer.analyze(t)
    )
