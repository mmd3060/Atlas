from core.state.conversation_state import ConversationState


state = ConversationState()


state.set_task(
    "Build Atlas OS"
)


state.update(
    "Working on Brain modules"
)


print(
    state.get_state()
)
