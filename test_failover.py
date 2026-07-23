from core.api_pool.pool_manager import APIPoolManager


pool = APIPoolManager()


pool.add_key("gemini", "KEY_1")
pool.add_key("gemini", "KEY_2")


print("First:")
print(pool.get_key("gemini"))


# خراب شدن KEY_1
pool.mark_failed("gemini", "KEY_1")


print("\nAfter failure:")
print(pool.get_key("gemini"))


print("\nStatus:")
print(pool.show_status())
