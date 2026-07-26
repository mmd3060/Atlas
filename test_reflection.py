from core.brain.reflection import ReflectionEngine


engine = ReflectionEngine()


result = engine.review(
    "This is a good answer",
    {
        "type":"code"
    }
)


print(result)
