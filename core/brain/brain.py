from core.brain.planner import Planner
from core.brain.reflection import ReflectionEngine
from core.brain.self_critic import SelfCritic



class AtlasBrain:


    def __init__(self):

        self.planner = Planner()

        self.reflection = ReflectionEngine()

        self.critic = SelfCritic()



    def process(
        self,
        answer,
        analysis
    ):


        plan = self.planner.create_plan(
            analysis
        )


        reflection = self.reflection.review(
            answer,
            analysis["task"]
        )


        critic = self.critic.critique(
            answer,
            analysis["task"]
        )


        return {

            "plan": plan,

            "reflection": reflection,

            "critic": critic

        }
