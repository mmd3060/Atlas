class ModelRegistry:


    def __init__(self):


        self.models = {


            "gpt-4.1": {

                "provider": "github",

                "capabilities": {

                    "code": 10,
                    "math": 9,
                    "text": 9,
                    "vision": 8,
                    "reasoning": 10

                }

            },


            "gemini-2.5-pro": {

                "provider": "gemini",

                "capabilities": {

                    "code": 8,
                    "math": 10,
                    "text": 9,
                    "vision": 10,
                    "reasoning": 10

                }

            },


            "qwen-coder": {

                "provider": "nvidia",

                "capabilities": {

                    "code": 10,
                    "math": 8,
                    "text": 7,
                    "vision": 5,
                    "reasoning": 8

                }

            }


        }



    def get_model(self, name):

        return self.models.get(name)



    def get_provider(self, name):

        model = self.get_model(name)

        if not model:

            return None


        return model["provider"]



    def list_models(self):

        return self.models
