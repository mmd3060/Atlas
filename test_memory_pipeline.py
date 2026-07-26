from core.memory.memory_pipeline import MemoryPipeline



pipeline = MemoryPipeline()



tests = [

    "سلام Atlas",

    "اسم من محمد است",

    "من دارم پروژه Atlas OS را می سازم",

    "این خطا قبلا مشکل ایجاد کرده بود"

]



for item in tests:

    print("\nINPUT:")
    print(item)

    result = pipeline.process(
        item
    )

    print(result)



print("\nMEMORY:")
print(
    pipeline.memory.get_context()
)
