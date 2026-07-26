from core.brain.planner import Planner
from core.brain.task_decomposer import TaskDecomposer
from core.brain.reflection import ReflectionEngine
from core.brain.self_critic import SelfCritic
from core.brain.confidence_engine import ConfidenceEngine
from core.brain.response_synthesizer import ResponseSynthesizer
from core.brain.error_recovery import ErrorRecovery

from core.intelligence.model_executor import ModelExecutor
from core.intelligence.multi_model_executor import MultiModelExecutor



class BrainPipeline:


    def __init__(self):

        self.planner = Planner()

        self.decomposer = TaskDecomposer()

        self.executor = ModelExecutor()

        self.multi_executor = MultiModelExecutor()

        self.synthesizer = ResponseSynthesizer()

        self.reflection = ReflectionEngine()

        self.critic = SelfCritic()

        self.confidence = ConfidenceEngine()

        self.recovery = ErrorRecovery()



    def run(
        self,
        analysis,
        decision,
        messages
    ):


        task = analysis.get(
            "task",
            {}
        )


        print(
            "🧠 Atlas Brain Pipeline Started"
        )


        # Planning

        plan = self.planner.create_plan(
            analysis
        )


        # Decomposition

        decomposition = None


        if task.get("difficulty") == "high":

            decomposition = self.decomposer.decompose(
                task
            )



        # Execution

        if decision.get(
            "use_multi_model"
        ):

            execution_data = self.multi_executor.execute(
                decision,
                messages
            )

            execution = execution_data.get(
                "results",
                []
            )


        else:

            execution = [
                self.executor.execute(
                    decision,
                    messages
                )
            ]



        # Error Recovery Analysis

        recovery = []


        for result in execution:

            recovery.append(
                self.recovery.analyze(
                    result
                )
            )



        # Synthesis

        answer = self.synthesizer.synthesize(
            execution
        )



        final_answer = answer.get(
            "answer"
        )



        # Reflection

        reflection = self.reflection.review(
            final_answer,
            task
        )



        # Critic

        critic = self.critic.critique(
            final_answer,
            task
        )



        # Confidence

        confidence = self.confidence.calculate(
            execution
        )


        print(
            "✅ Atlas Brain Pipeline Finished"
        )


        return {

            "plan": plan,

            "decomposition": decomposition,

            "execution": execution,

            "recovery": recovery,

            "answer": answer,

            "reflection": reflection,

            "critic": critic,

            "confidence": confidence

        }
