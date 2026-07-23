from core.router.smart_router import SmartRouter


router = SmartRouter()


messages = [
    "این کد python مشکل دارد",
    "حل کن: 2+2= ؟",
    "سلام حالت چطوره"
]


for msg in messages:
    result = router.route(msg)

    print("\nMessage:")
    print(msg)

    print("Decision:")
    print(result)
