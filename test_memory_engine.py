from core.memory.memory_engine import MemoryEngine

memory = MemoryEngine()

memory.save(
    "project",
    "name",
    "Atlas OS"
)

memory.save(
    "user",
    "developer",
    "MMD42960"
)

memory.save(
    "session",
    "current_module",
    "Memory Engine"
)

print(memory.load(
    "project",
    "name"
))

print(memory.load(
    "user",
    "developer"
))

print(memory.get_context())
