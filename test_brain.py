from core.brain.brain import AtlasBrain


brain = AtlasBrain()


result = brain.process(

    """
    ```python
    print("hello")
    ```
    """,

    {
        "task":
        {
            "type":"code",
            "difficulty":"normal",
            "requires_tool":False
        }
    }

)


print(result)
