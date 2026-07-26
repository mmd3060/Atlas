from core.memory.context_manager import ContextManager


context = ContextManager()


context.update(
    "user",
    {
        "name": "محمد",
        "goal": "Build Atlas OS"
    }
)


context.update(
    "project",
    {
        "name": "Atlas",
        "version": "v0.6"
    }
)


context.update(
    "conversation",
    {
        "topic": "Memory System"
    }
)


print(
    context.get_context()
)


print(
    context.build_prompt_context()
)
