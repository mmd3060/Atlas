class PersonalityEngine:


    def __init__(self):

        self.profile = {

            "name": "Atlas",

            "owner": "محمد",

            "tone": "friendly",

            "style": "natural",

            "emoji": True

        }



    def get_profile(self):

        return self.profile



    def set_tone(
        self,
        tone
    ):

        self.profile["tone"] = tone



    def format_response(
        self,
        answer,
        context=None
    ):


        if not answer:

            return answer



        prefix = ""



        # حالت دوستانه Atlas

        if self.profile["tone"] == "friendly":

            if context:

                prefix = f"{self.profile['owner']} 😎، "



        response = prefix + answer



        return response



    def adapt(
        self,
        user_preference
    ):


        if "formal" in user_preference:

            self.profile["tone"] = "formal"



        elif "casual" in user_preference:

            self.profile["tone"] = "friendly"



        return self.profile
