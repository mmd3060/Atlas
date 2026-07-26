from core.memory.memory_coordinator import MemoryCoordinator


memory = MemoryCoordinator()


print(
    memory.build_context(
        "MMD42960",
        "ادامه ساخت Atlas"
    )
)


print(
    memory.update(
        "user",
        "ساخت Memory Coordinator"
    )
)
