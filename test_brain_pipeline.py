from core.brain.brain_pipeline import BrainPipeline


pipeline = BrainPipeline()


analysis = {

    "task": {

        "type": "text",

        "difficulty": "low",

        "requires_tool": False

    }

}


decision = {

    "model": "gpt-4.1",

    "use_multi_model": False

}


messages = [

    {

        "role": "user",

        "content": "سلام حالت چطوره؟"

    }

]


result = pipeline.run(
    analysis,
    decision,
    messages
)


print(result)
