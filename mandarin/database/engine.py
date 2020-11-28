import sqlalchemy
import sqlalchemy.orm

from ..config import *
# noinspection PyUnresolvedReferences
from .tables import *


engine = sqlalchemy.create_engine(config["database.uri"])
Session = sqlalchemy.orm.sessionmaker(bind=engine)


__all__ = (
    "engine",
    "Session",
)
