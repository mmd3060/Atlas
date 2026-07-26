from core.brain.planner import Planner

planner = Planner()

analysis = {
    "task": {
        "type": "reasoning",
        "difficulty": "high",
        "requires_tool": False
    }
}

plan = planner.create_plan(
    analysis
)

print(plan)
