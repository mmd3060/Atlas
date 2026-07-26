from dotenv import load_dotenv

load_dotenv()


from core.intelligence.model_executor import ModelExecutor
from core.intelligence.intelligence_engine import IntelligenceEngine
from core.intelligence.decision_engine import DecisionEngine



engine = IntelligenceEngine()

decision_engine = DecisionEngine()

executor = ModelExecutor()



message = "write python api for telegram bot"



analysis = engine.analyze(
    message
)



decision = decision_engine.decide(
    analysis
)



print("================")
print("Decision:")
print(decision)



result = executor.execute(
    decision,
    [
        {
            "role": "user",
            "content": message
        }
    ]
)



print("================")
print("Execution Result:")
print(result)
