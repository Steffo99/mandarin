celery_timeout = {
    202: {"description": "Task queued, but didn't finish in less than 5 seconds"}
}

login_error = {
    401: {"description": "Not logged in"},
}


__all__ = (
    "celery_timeout",
    "login_error",
)