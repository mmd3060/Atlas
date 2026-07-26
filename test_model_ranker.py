from core.models.model_ranker import ModelRanker


ranker = ModelRanker()


tasks = [

    "code",

    "math",

    "text",

    "vision"

]


for task in tasks:

    print("\n====================")

    print(

        "Task:",

        task

    )

    ranking = ranker.rank(
        task
    )

    for item in ranking:

        print(

            f"{item['model']}  ->  {item['score']}"

        )

    print(

        "\nWinner:",

        ranker.best_model(
            task
        )["model"]

    )
