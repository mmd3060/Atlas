from core.brain.error_recovery import ErrorRecovery


recovery = ErrorRecovery()


result = {

    "status": "failed",

    "error": "Missing credentials api_key"

}


print(
    recovery.analyze(result)
)
