from core.api_pool.pool_manager import APIPoolManager


pool = APIPoolManager()


pool.add_key("gemini", "KEY_1")
pool.add_key("gemini", "KEY_2")


print(pool.get_key("gemini"))
print(pool.get_key("gemini"))
print(pool.get_key("gemini"))


print(pool.show_status())
