from core.brain.response_synthesizer import ResponseSynthesizer

s = ResponseSynthesizer()

results = [
    {
        "model": "gpt-4.1",
        "provider": "github",
        "status": "success",
        "answer": "Answer from GPT"
    },
    {
        "model": "gemini-2.5-pro",
        "provider": "gemini",
        "status": "success",
        "answer": "Answer from Gemini"
    }
]

print(s.synthesize(results))
