import time
import uuid
from copy import deepcopy


class ConversationState:
    """
    Core Conversation State Model

    Atlas OS Memory Foundation
    """

    def __init__(
        self,
        conversation_id=None
    ):

        now = time.time()

        self.data = {

            "conversation_id":
                conversation_id or self.generate_id(),

            "created_at": now,

            "updated_at": now,


            "messages": [],


            "context": {

                "topic": None,

                "goal": None,

                "summary": None

            },


            "user_context": {

                "name": None,

                "preferences": {},

                "facts": {}

            },


            "project_context": {

                "name": None,

                "version": None,

                "module": None

            },


            "brain_state": {

                "last_task": None,

                "difficulty": None,

                "decision": None

            },


            "execution": {

                "last_model": None,

                "last_provider": None,

                "last_tool": None

            },


            "events": [],


            "step": 0,


            "metadata": {}

        }


    def generate_id(self):

        return (
            "conv-"
            +
            str(uuid.uuid4())[:8]
        )


    def update_timestamp(self):

        self.data["updated_at"] = time.time()


    def snapshot(self):

        return deepcopy(
            self.data
        )





class ConversationStateManager:


    def __init__(self):

        self.state = ConversationState()



    def reset(self):

        self.state = ConversationState()



    # Compatibility

    def set_conversation_id(
        self,
        conversation_id
    ):

        self.state.data["conversation_id"] = conversation_id

        self.state.update_timestamp()



    # Messages

    def add_message(
        self,
        role,
        content,
        metadata=None
    ):

        self.state.data["messages"].append({

            "role": role,

            "content": content,

            "time": time.time(),

            "metadata": metadata or {}

        })


        self.state.data["step"] += 1

        self.add_event(
            "message_added"
        )


        self.state.update_timestamp()



    def get_messages(self):

        return self.state.data["messages"]



    # Context

    def set_topic(
        self,
        topic
    ):

        self.state.data["context"]["topic"] = topic

        self.state.update_timestamp()



    def get_topic(self):

        return self.state.data["context"]["topic"]



    def set_goal(
        self,
        goal
    ):

        self.state.data["context"]["goal"] = goal

        self.state.update_timestamp()



    def get_goal(self):

        return self.state.data["context"]["goal"]



    def set_summary(
        self,
        summary
    ):

        self.state.data["context"]["summary"] = summary

        self.state.update_timestamp()



    def get_context(self):

        return self.state.data["context"]



    # User

    def update_user_context(
        self,
        key,
        value
    ):

        self.state.data["user_context"][key] = value

        self.state.update_timestamp()



    def get_user_context(self):

        return self.state.data["user_context"]



    # Project

    def update_project_context(
        self,
        key,
        value
    ):

        self.state.data["project_context"][key] = value

        self.state.update_timestamp()



    def get_project_context(self):

        return self.state.data["project_context"]



    # Brain

    def update_brain_state(
        self,
        key,
        value
    ):

        self.state.data["brain_state"][key] = value

        self.state.update_timestamp()



    def get_brain_state(self):

        return self.state.data["brain_state"]



    # Execution

    def set_last_execution(
        self,
        model,
        provider,
        tool=None
    ):

        self.state.data["execution"] = {

            "last_model": model,

            "last_provider": provider,

            "last_tool": tool

        }

        self.state.update_timestamp()



    # Old compatibility

    def set_last_model(
        self,
        model,
        provider=None
    ):

        self.set_last_execution(
            model,
            provider
        )


    def set_last_tool(
        self,
        tool
    ):

        self.state.data["execution"]["last_tool"] = tool

        self.state.update_timestamp()



    def set_module(
        self,
        module
    ):

        self.state.data["project_context"]["module"] = module

        self.state.update_timestamp()



    # Events

    def add_event(
        self,
        event
    ):

        self.state.data["events"].append({

            "event": event,

            "time": time.time()

        })



    # Metadata

    def set_metadata(
        self,
        key,
        value
    ):

        self.state.data["metadata"][key] = value

        self.state.update_timestamp()



    def get_metadata(
        self,
        key,
        default=None
    ):

        return self.state.data["metadata"].get(
            key,
            default
        )



    def snapshot(self):

        return self.state.snapshot()
