class MemoryEngine:
    """
    Memory Engine v2

    هسته ذخیره‌سازی حافظه Atlas OS.

    مسئول:
    - ذخیره اطلاعات
    - بازیابی اطلاعات
    - مدیریت انواع حافظه
    """

    def __init__(self):

        self.short_memory = {}

        self.long_memory = {}

        self.session_memory = {}

        self.project_memory = {}

        self.user_memory = {}

        self.task_memory = {}

        self.experience_memory = {}

        self.knowledge_memory = {}



    # -------------------------
    # Save
    # -------------------------

    def save(
        self,
        category,
        key,
        value
    ):

        memory = self._get_memory(
            category
        )

        memory[key] = value



    # -------------------------
    # Load
    # -------------------------

    def load(
        self,
        category,
        key,
        default=None
    ):

        memory = self._get_memory(
            category
        )

        return memory.get(
            key,
            default
        )



    # -------------------------
    # Update
    # -------------------------

    def update(
        self,
        category,
        key,
        value
    ):

        self.save(
            category,
            key,
            value
        )



    # -------------------------
    # Delete
    # -------------------------

    def delete(
        self,
        category,
        key
    ):

        memory = self._get_memory(
            category
        )

        if key in memory:

            del memory[key]



    # -------------------------
    # Clear
    # -------------------------

    def clear_session(self):

        self.session_memory.clear()



    # -------------------------
    # Context Export
    # -------------------------

    def get_context(self):

        return {

            "short": self.short_memory,

            "long": self.long_memory,

            "session": self.session_memory,

            "project": self.project_memory,

            "user": self.user_memory,

            "task": self.task_memory,

            "experience": self.experience_memory,

            "knowledge": self.knowledge_memory

        }



    # -------------------------
    # Internal Router
    # -------------------------

    def _get_memory(
        self,
        category
    ):

        mapping = {

            "short":
                self.short_memory,

            "long":
                self.long_memory,

            "session":
                self.session_memory,

            "project":
                self.project_memory,

            "user":
                self.user_memory,

            "task":
                self.task_memory,

            "experience":
                self.experience_memory,

            "knowledge":
                self.knowledge_memory

        }


        return mapping.get(
            category,
            self.short_memory
        )
