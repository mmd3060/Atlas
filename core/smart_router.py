"""
Atlas Smart Router
Decides which AI provider should handle each task.
"""

from dataclasses import dataclass


@dataclass
class TaskInfo:
    category: str
    reason: str


def detect_task(message: str) -> TaskInfo:

    text = message.lower()


    # Programming
    code_words = [
        "python",
        "کد",
        "برنامه",
        "خطا",
        "error",
        "bug",
        "debug",
        "function",
        "class",
    ]

    if any(word in text for word in code_words):

        return TaskInfo(
            category="coding",
            reason="Programming related request"
        )


    # Math / Science
    science_words = [
        "ریاضی",
        "فیزیک",
        "شیمی",
        "فرمول",
        "محاسبه",
    ]

    if any(word in text for word in science_words):

        return TaskInfo(
            category="science",
            reason="Scientific question"
        )


    # Translation / Language
    language_words = [
        "ترجمه",
        "انگلیسی",
        "meaning",
        "grammar",
    ]

    if any(word in text for word in language_words):

        return TaskInfo(
            category="language",
            reason="Language request"
        )


    return TaskInfo(
        category="general",
        reason="General conversation"
    )



def choose_provider(task: TaskInfo):

    if task.category == "coding":
        return "github"


    if task.category == "science":
        return "openrouter"


    if task.category == "language":
        return "openrouter"


    return "openrouter"
