MAX_MESSAGE_LENGTH = 4000


def split_message(text):

    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]

    parts = []

    while len(text) > MAX_MESSAGE_LENGTH:

        split_at = text.rfind(
            "\n",
            0,
            MAX_MESSAGE_LENGTH
        )

        if split_at == -1:
            split_at = MAX_MESSAGE_LENGTH

        parts.append(
            text[:split_at]
        )

        text = text[split_at:]

    if text:
        parts.append(text)

    return parts
