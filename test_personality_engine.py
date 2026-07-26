from core.personality.personality_engine import PersonalityEngine


atlas = PersonalityEngine()


print(
    atlas.get_profile()
)


answer = atlas.format_response(
    "مشکل کد پیدا شد.",
    context=True
)


print(answer)


atlas.adapt(
    "casual"
)


print(
    atlas.get_profile()
)
