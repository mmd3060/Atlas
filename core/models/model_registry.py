class ModelRegistry:


    def __init__(self):


        self.models = {


            "gpt-4.1": {


                "providers": [
                    "github",
                    "openrouter"
                ],


                "skills": {

                    "code": 10,
                    "math": 9,
                    "text": 9,
                    "vision": 8

                },


                "cost": 7,
                "context": 10

            },



            "gemini-2.5-pro": {


                "providers": [
                    "google",
                    "openrouter"
                ],


                "skills": {

                    "code": 8,
                    "math": 10,
                    "text": 9,
                    "vision": 10

                },


                "cost": 9,
                "context": 10

            },



            "qwen-coder": {


                "providers": [
                    "nvidia",
                    "openrouter"
                ],


                "skills": {

                    "code": 10,
                    "math": 8,
                    "text": 7,
                    "vision": 5

                },


                "cost": 10,
                "context": 8

            }


        }



    def get_models(self):

        return self.models
