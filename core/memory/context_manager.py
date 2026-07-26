class ContextManager:


    def __init__(self):

        self.context = {

            "user": {},

            "conversation": {},

            "project": {},

            "system": {}

        }



    def update(
        self,
        key,
        value
    ):

        if key in self.context:

            self.context[key].update(
                value
            )



    def get_context(self):

        return self.context



    def build_prompt_context(self):

        return {

            "user_context":
                self.context["user"],

            "conversation_context":
                self.context["conversation"],

            "project_context":
                self.context["project"],

            "system_context":
                self.context["system"]

        }
