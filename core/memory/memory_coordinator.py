import time


from core.memory.memory_engine import MemoryEngine
from core.memory.conversation_state import ConversationStateManager
from core.memory.context_manager import ContextManager
from core.memory.memory_pipeline import MemoryPipeline



class MemoryCoordinator:
    """
    Memory Coordinator v2.0

    مرکز هماهنگی Memory System در Atlas OS.

    مسئولیت:

    - مدیریت Conversation State
    - مدیریت Context
    - اجرای Memory Pipeline
    - اتصال Memory Engine
    - آماده سازی حافظه برای Brain
    """



    def __init__(self):

        # حافظه مرکزی

        self.memory = MemoryEngine()


        # وضعیت مکالمه

        self.state = ConversationStateManager()


        # Context

        self.context = ContextManager()


        # Pipeline با همان MemoryEngine

        self.pipeline = MemoryPipeline(
            self.memory
        )



    # ---------------------------------
    # Process Message
    # ---------------------------------

    def process_message(
        self,
        user_id,
        message
    ):

        # ثبت پیام کاربر

        self.state.add_message(
            "user",
            message
        )


        # پردازش حافظه

        memory_result = self.pipeline.process(
            message
        )


        # ساخت context

        context = self.build_context(
            user_id,
            message
        )


        return {

            "status": "processed",

            "user_id": user_id,

            "message": message,

            "memory": memory_result,

            "context": context

        }



    # ---------------------------------
    # Build Context
    # ---------------------------------

    def build_context(
        self,
        user_id,
        message
    ):

        return {

            "user_id": user_id,

            "message": message,

            "conversation":
                self.state.snapshot(),

            "context":
                self.context.get_context(),

            "memory":
                self.memory.get_context(),

            "timestamp":
                time.time()

        }



    # ---------------------------------
    # Add Message
    # ---------------------------------

    def add_message(
        self,
        role,
        content,
        metadata=None
    ):

        self.state.add_message(
            role,
            content,
            metadata
        )


        return {

            "status": "success",

            "event": "message_added",

            "role": role

        }



    # ---------------------------------
    # Update Context
    # ---------------------------------

    def update_context(
        self,
        category,
        data
    ):

        self.context.update(
            category,
            data
        )


        return {

            "status": "updated",

            "category": category

        }



    # ---------------------------------
    # Memory Operations
    # ---------------------------------

    def save_memory(
        self,
        category,
        key,
        value
    ):

        self.memory.save(
            category,
            key,
            value
        )


        return {

            "status": "saved",

            "category": category,

            "key": key

        }



    def load_memory(
        self,
        category,
        key,
        default=None
    ):

        return self.memory.load(
            category,
            key,
            default
        )



    # ---------------------------------
    # Export
    # ---------------------------------

    def snapshot(self):

        return {

            "conversation":
                self.state.snapshot(),

            "context":
                self.context.get_context(),

            "memory":
                self.memory.get_context()

        }
