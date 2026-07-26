from core.brain.brain_engine import BrainEngine


brain = BrainEngine()


analysis = {

    "task": {

        "requires_tool": False,
        "difficulty": "high"

    }

}


print(
    brain.think(
        analysis
    )
)
