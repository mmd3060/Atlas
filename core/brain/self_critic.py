class SelfCritic:


    def critique(
        self,
        answer,
        task
    ):


        issues = []


        task_type = task.get(
            "type",
            "text"
        )


        # بررسی جواب خالی

        if not answer:

            issues.append(
                "empty_response"
            )


            return {

                "critic_score": 0,

                "issues": issues,

                "approved": False

            }



        # بررسی طول جواب

        if len(answer) < 20:

            issues.append(
                "short_response"
            )



        # بررسی کد

        if task_type == "code":

            if "```" not in answer:

                issues.append(
                    "code_format_missing"
                )



        # بررسی ریاضی

        if task_type == "math":

            if "=" not in answer:

                issues.append(
                    "missing_solution_steps"
                )



        # محاسبه امتیاز

        score = 100 - (
            len(issues) * 15
        )


        if score < 0:

            score = 0



        return {

            "critic_score": score,

            "issues": issues,

            "approved": score >= 70

        }
