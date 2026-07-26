from core.intelligence.model_ranker import ModelRanker


ranker = ModelRanker()


tests = [

    "code",
    "math",
    "text",
    "vision"

]


for task in tests:

    print("\n================")

    print(
        "Task:",
        task
    )


    print(
        ranker.rank(task)
    )


    print(
        "Winner:",
        ranker.best_model(task)
    )
