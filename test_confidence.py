from core.brain.confidence_engine import ConfidenceEngine


engine = ConfidenceEngine()



results = [

    {
        "model":"gpt-4.1",
        "status":"success",
        "answer":"x=-2,-3"
    },


    {
        "model":"gemini-2.5-pro",
        "status":"success",
        "answer":"x=-2,-3"
    }

]


print(
    engine.calculate(results)
)
