from core.analyzer.message_analyzer import MessageAnalyzer
from core.api_pool.pool_manager import APIPoolManager
from core.health.provider_health import ProviderHealthMonitor
from core.decision.decision_engine import DecisionEngine
from core.cost.token_analyzer import TokenAnalyzer



class SmartRouter:


    def __init__(self):

        self.analyzer = MessageAnalyzer()

        self.cost = TokenAnalyzer()

        self.api_pool = APIPoolManager()

        self.health = ProviderHealthMonitor()

        self.brain = DecisionEngine()



        providers = [

            "github",
            "gemini",
            "openrouter"

        ]


        for provider in providers:

            self.health.register_provider(
                provider
            )



        # Test API Keys

        self.api_pool.add_key(
            "github",
            "GITHUB_KEY_1"
        )


        self.api_pool.add_key(
            "gemini",
            "GEMINI_KEY_1"
        )


        self.api_pool.add_key(
            "gemini",
            "GEMINI_KEY_2"
        )




    def get_provider_profiles(self):


        return {


            "github": {


                "code": {

                    "quality": 10,
                    "speed": 8,
                    "cost": 7,
                    "health": 10,
                    "context": 8

                },


                "math": {

                    "quality": 6,
                    "speed": 7,
                    "cost": 7,
                    "health": 10,
                    "context": 8

                },


                "text": {

                    "quality": 7,
                    "speed": 8,
                    "cost": 8,
                    "health": 10,
                    "context": 8

                },


                "long_generation": {

                    "quality": 7,
                    "speed": 7,
                    "cost": 7,
                    "health": 10,
                    "context": 8

                }

            },



            "gemini": {


                "code": {

                    "quality": 8,
                    "speed": 10,
                    "cost": 9,
                    "health": 10,
                    "context": 10

                },


                "math": {

                    "quality": 10,
                    "speed": 9,
                    "cost": 8,
                    "health": 10,
                    "context": 10

                },


                "text": {

                    "quality": 9,
                    "speed": 10,
                    "cost": 9,
                    "health": 10,
                    "context": 10

                },


                "long_generation": {

                    "quality": 10,
                    "speed": 8,
                    "cost": 8,
                    "health": 10,
                    "context": 10

                }

            },



            "openrouter": {


                "code": {

                    "quality": 8,
                    "speed": 8,
                    "cost": 8,
                    "health": 10,
                    "context": 10

                },


                "math": {

                    "quality": 9,
                    "speed": 8,
                    "cost": 8,
                    "health": 10,
                    "context": 10

                },


                "text": {

                    "quality": 8,
                    "speed": 8,
                    "cost": 8,
                    "health": 10,
                    "context": 10

                },


                "long_generation": {

                    "quality": 9,
                    "speed": 7,
                    "cost": 8,
                    "health": 10,
                    "context": 10

                }

            }

        }





    def route(self, message):


        analysis = self.analyzer.analyze(
            message
        )


        task = analysis["type"]



        cost_analysis = self.cost.analyze(
            message
        )


        complexity = cost_analysis["complexity"]



        all_profiles = self.get_provider_profiles()



        # استخراج پروفایل مخصوص همین Task

        candidates = {}


        for name, profile in all_profiles.items():

            candidates[name] = profile.get(
                task,
                profile["text"]
            )



        decision = self.brain.choose_best(

            candidates,

            task,

            complexity

        )



        provider = decision["provider"]



        health_status = self.health.get_status(
            provider
        )



        if health_status["status"] != "healthy":

            provider = "gemini"




        return {


            "analysis": analysis,

            "cost": cost_analysis,

            "task": task,

            "complexity": complexity,

            "provider": provider,

            "score": decision["score"],

            "api_key": self.api_pool.get_key(
                provider
            ),

            "health": self.health.get_status(
                provider
            )

        }
