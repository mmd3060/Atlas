def get_memory_prompt(user_id=None):
    """
    Temporary compatibility layer
    تا زمان ساخت Memory Engine اصلی Atlas
    """

    return ""


def add_message(
    user_id,
    role,
    content
):
    """
    Temporary memory stub
    """

    return [
        {
            "role": role,
            "content": content
        }
    ]
