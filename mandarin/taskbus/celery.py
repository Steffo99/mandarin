import celery

from ..config import config


app = celery.Celery("mandarin",
                    broker=config["taskbus.broker"],
                    backend=config["taskbus.backend"],
                    include=["mandarin.taskbus.tasks"])

__all__ = (
    "app",
)
