from core.brain.self_critic import SelfCritic


critic = SelfCritic()


result = critic.critique(
    """
    ```python
    print("hello")
    ```
    """,
    {
        "type":"code"
    }
)


print(result)
