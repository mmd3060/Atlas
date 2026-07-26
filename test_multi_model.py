from dotenv import load_dotenv

load_dotenv()


from core.intelligence.intelligence_engine import IntelligenceEngine
from core.intelligence.decision_engine import DecisionEngine
from core.intelligence.multi_model_executor import MultiModelExecutor



engine = IntelligenceEngine()

decision_engine = DecisionEngine()

executor = MultiModelExecutor()



message = "طراحی معماری یک AI Agent حرفه‌ای"



analysis = engine.analyze(
    message
)


decision = decision_engine.decide(
    analysis
)


print("================")
print(decision)



if decision["use_multi_model"]:


    result = executor.execute(
        decision,
        [
            {
                "role":"user",
                "content":message
            }
        ]
    )


    print("================")
    print(result)


else:

    print(
        "Single model mode"
    )
