import celery as _celery

from ..config import config


celery = _celery.Celery(__name__, broker=config["taskbus.broker"], backend=config["taskbus.backend"])


__all__ = (
    "celery",
)
