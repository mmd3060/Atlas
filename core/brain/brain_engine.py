from core.brain.planner import Planner
from core.brain.decomposer import TaskDecomposer
from core.brain.reflection import ReflectionEngine
from core.brain.self_critic import SelfCritic


class BrainEngine:


    def __init__(self):

        self.planner = Planner()

        self.decomposer = TaskDecomposer()

        self.reflection = ReflectionEngine()

        self.critic = SelfCritic()



    def think(
        self,
        analysis
    ):


        task = analysis["task"]


        # ساخت برنامه انجام کار

        plan = self.planner.create_plan(
            analysis
        )


        # شکستن کارهای سخت

        decomposition = None


        if task.get("difficulty") == "high":

            decomposition = self.decomposer.decompose(
                task
            )



        result = {


            "plan": plan,

            "decomposition": decomposition,

            "reflection": None,

            "critic": None

        }



        # فعلاً جواب آزمایشی
        # بعداً به Executor و Synthesizer وصل می‌شود

        temporary_answer = (
            "temporary answer"
        )



        result["reflection"] = self.reflection.review(
            temporary_answer,
            task
        )



        result["critic"] = self.critic.critique(
            temporary_answer,
            task
        )



        return result
