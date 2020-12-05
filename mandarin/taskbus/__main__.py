import celery

from ..config import lazy_config


class CeleryConfig:
    @property
    def broker_url(self):
        return lazy_config.e["taskbus.broker"]

    @property
    def result_backend(self):
        return lazy_config.e["taskbus.backend"]

    imports = ["mandarin.taskbus.tasks"]
    task_serializer = "pickle"
    accept_content = ["application/json", "application/x-python-serialize"]


app = celery.Celery("mandarin")
app.config_from_object(CeleryConfig)


__all__ = (
    "app",
)
