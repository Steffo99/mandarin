from royalnet.typing import *
import sqlalchemy
import sqlalchemy.orm

from ..config import *
from ..database import *


engine = sqlalchemy.create_engine(config["database.uri"])
Base.metadata.bind = engine
Session = sqlalchemy.orm.sessionmaker(bind=engine)


__all__ = (
    "engine",
    "Session",
)
