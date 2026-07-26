class Planner:

    def create_plan(self, analysis):

        task = analysis["task"]

        plan = []

        # مرحله اول
        plan.append("understand_request")

        # حافظه
        plan.append("load_memory")

        # ابزار
        if task["requires_tool"]:
            plan.append("select_tool")

        # کار سخت
        if task["difficulty"] == "high":
            plan.append("decompose_task")

            plan.append("multi_reasoning")

        # تولید پاسخ
        plan.append("generate_answer")

        # بررسی
        plan.append("self_review")

        return {
            "steps": plan,
            "count": len(plan)
        }
