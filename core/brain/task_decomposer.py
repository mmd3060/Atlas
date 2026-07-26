class TaskDecomposer:

    def decompose(self, message):

        words = len(message.split())

        if words < 10:
            return [message]

        return [
            "Analyze problem",
            "Break into sub tasks",
            "Solve each task",
            "Merge results",
            "Final review"
        ]
