from core.memory.conversation_state import ConversationStateManager


state = ConversationStateManager()

state.set_conversation_id("atlas-test")

state.set_topic("Brain")

state.set_goal("Build Conversation Manager")

state.set_module("Memory")

state.set_last_model(
    "gpt-4.1",
    "github"
)

state.add_message(
    "user",
    "سلام Atlas"
)

state.add_message(
    "assistant",
    "سلام محمد 😎"
)

print(state.snapshot())
