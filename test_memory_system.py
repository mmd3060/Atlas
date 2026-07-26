from core.memory.memory_coordinator import MemoryCoordinator


memory = MemoryCoordinator()


messages = [

    "سلام Atlas",

    "اسم من محمد است",

    "من دارم پروژه Atlas OS را می سازم",

    "این خطا قبلا مشکل ایجاد کرده بود"

]


for msg in messages:

    print("\nINPUT:")
    print(msg)

    result = memory.process_message(
        "MMD42960",
        msg
    )

    print(result)



print("\nFINAL MEMORY:")
print(
    memory.memory.get_context()
)
