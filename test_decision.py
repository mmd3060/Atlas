from core.decision.decision_engine import DecisionEngine


brain = DecisionEngine()


providers = {

    "github": {

        "quality": 9,
        "speed": 7,
        "cost": 6,
        "health": 10

    },


    "gemini": {

        "quality": 8,
        "speed": 10,
        "cost": 9,
        "health": 10

    }

}



print(
    brain.choose_best(providers)
)
