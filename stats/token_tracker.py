import json
import os
from datetime import datetime


STATS_FILE = "stats/token_usage.json"


def load_stats():

    if not os.path.exists(STATS_FILE):
        return {}

    try:
        with open(
            STATS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (json.JSONDecodeError, ValueError):
        return {}



def save_stats(stats):

    with open(
        STATS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            stats,
            file,
            ensure_ascii=False,
            indent=4
        )



def track_usage(
    provider,
    model,
    prompt_tokens=0,
    completion_tokens=0
):

    stats = load_stats()


    if provider not in stats:

        stats[provider] = {
            "requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "last_used": None,
            "models": {}
        }


    data = stats[provider]


    data["requests"] += 1

    data["prompt_tokens"] += prompt_tokens

    data["completion_tokens"] += completion_tokens

    data["total_tokens"] += (
        prompt_tokens +
        completion_tokens
    )


    data["last_used"] = (
        datetime.now()
        .strftime("%Y-%m-%d %H:%M:%S")
    )


    if model not in data["models"]:
        data["models"][model] = 0


    data["models"][model] += 1


    save_stats(stats)



def get_usage():

    return load_stats()



def get_usage_report():

    stats = load_stats()

    if not stats:
        return "📊 هنوز آماری ثبت نشده."


    report = "📊 Atlas Token Usage\n\n"


    for provider, data in stats.items():

        report += (
            f"🤖 {provider}\n"
            f"Requests: {data['requests']}\n"
            f"Prompt: {data['prompt_tokens']}\n"
            f"Completion: {data['completion_tokens']}\n"
            f"Total: {data['total_tokens']}\n"
            f"Last used: {data['last_used']}\n\n"
        )


    return report
