import sqlalchemy.orm
import royalnet.lazy as l

from ..config import *
# noinspection PyUnresolvedReferences
from .tables import *


lazy_engine = l.Lazy(lambda c: sqlalchemy.create_engine(c["database.uri"]), c=lazy_config)
lazy_Session = l.Lazy(lambda e: sqlalchemy.orm.sessionmaker(bind=e), e=lazy_engine)


__all__ = (
    "lazy_engine",
    "lazy_Session",
)
