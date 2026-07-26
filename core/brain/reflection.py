class ReflectionEngine:


    def review(
        self,
        answer,
        task
    ):


        issues = []


        if not answer:

            issues.append(
                "empty_answer"
            )

            return {

                "quality": 0,

                "issues": issues,

                "needs_revision": True

            }



        if len(answer) < 20:

            issues.append(
                "short_answer"
            )



        task_type = task.get(
            "type",
            "text"
        )


        # بررسی ساده کیفیت برای کد

        if task_type == "code":

            if "```" not in answer:

                issues.append(
                    "missing_code_block"
                )



        # بررسی ریاضی

        if task_type == "math":

            if "=" not in answer:

                issues.append(
                    "missing_equation_steps"
                )



        quality = 100 - (
            len(issues) * 20
        )


        if quality < 0:

            quality = 0



        return {

            "quality": quality,

            "issues": issues,

            "needs_revision": quality < 70

        }
