import sqlalchemy.orm
import royalnet.lazy

from ..config import *
# noinspection PyUnresolvedReferences
from . import tables


lazy_engine = royalnet.lazy.Lazy(lambda c: sqlalchemy.create_engine(c["database.uri"]), c=lazy_config)
"""
The uninitialized sqlalchemy engine.
"""

lazy_Session = royalnet.lazy.Lazy(lambda e: sqlalchemy.orm.sessionmaker(bind=e), e=lazy_engine)
"""
The uninitialized Session.
"""


__all__ = (
    "lazy_engine",
    "lazy_Session",
)
