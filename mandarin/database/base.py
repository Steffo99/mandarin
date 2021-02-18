import sqlalchemy.orm
import sqlalchemy_searchable
from sqlalchemy.ext.declarative import declarative_base

Base: declarative_base = declarative_base()
sqlalchemy_searchable.make_searchable(metadata=Base.metadata)

__all__ = (
    "Base",
)
