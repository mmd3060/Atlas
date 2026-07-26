from dotenv import load_dotenv

load_dotenv()


from core.intelligence.intelligence_engine import IntelligenceEngine
from core.intelligence.decision_engine import DecisionEngine


engine = IntelligenceEngine()
decision_engine = DecisionEngine()


tests = [
    "سلام حالت چطوره",
    "حل کن این معادله x^2+5x+6=0",
    "write python telegram bot api",
    "طراحی معماری یک AI Agent حرفه‌ای",
]


for message in tests:

    print("\n================")
    print(message)

    analysis = engine.analyze(message)

    decision = decision_engine.decide(
        analysis
    )

    print(decision)
