class ErrorRecovery:


    def analyze(
        self,
        execution_result
    ):


        error = execution_result.get(
            "error"
        )


        if not error:

            return {

                "recovery_needed": False,

                "action": "none",

                "reason": "no_error"

            }



        error_text = str(error).lower()



        # مشکل API Key

        if (
            "credential" in error_text
            or
            "api_key" in error_text
        ):

            return {

                "recovery_needed": True,

                "action": "switch_provider",

                "reason": "authentication_failure"

            }



        # مشکل زمان

        if (
            "timeout" in error_text
            or
            "time" in error_text
        ):

            return {

                "recovery_needed": True,

                "action": "retry",

                "reason": "timeout"

            }



        # مشکل مدل

        if "unknown model" in error_text:

            return {

                "recovery_needed": True,

                "action": "update_registry",

                "reason": "model_not_found"

            }



        return {

            "recovery_needed": True,

            "action": "unknown",

            "reason": "unclassified_error"

        }
