class ConversationState:


    def __init__(self):

        self.state = {

            "current_task": None,

            "last_message": None,

            "context": []

        }



    def update(
        self,
        message
    ):

        self.state["last_message"] = message

        self.state["context"].append(
            message
        )


        return self.state



    def set_task(
        self,
        task
    ):

        self.state["current_task"] = task



    def get_state(self):

        return self.state
