import celery

from ..config import config


class CeleryConfig:
    broker_url = config["taskbus.broker"]
    result_backend = config["taskbus.backend"]
    imports = ["mandarin.taskbus.tasks"]
    task_serializer = "pickle"
    accept_content = ["application/json", "application/x-python-serialize"]


app = celery.Celery("mandarin")
app.config_from_object(CeleryConfig)

__all__ = (
    "app",
)
