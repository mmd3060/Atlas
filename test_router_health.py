from core.router.smart_router import SmartRouter


router = SmartRouter()


print("=== Normal Request ===")

result = router.route(
    "این کد python مشکل دارد"
)

print(result)



print("\n=== Simulate GitHub Failure ===")


# خراب کردن GitHub
router.health.mark_error(
    "github",
    "API Timeout"
)

router.health.mark_error(
    "github",
    "Rate Limit"
)

router.health.mark_error(
    "github",
    "Server Error"
)



print("\nGitHub Health:")

print(
    router.health.get_status("github")
)



print("\n=== Request After Failure ===")


result = router.route(
    "این کد python مشکل دارد"
)


print(result)
