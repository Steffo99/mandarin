import celery as _celery

from ..config import config


app = _celery.Celery(__name__, broker=config["taskbus.broker"], backend=config["taskbus.backend"])
