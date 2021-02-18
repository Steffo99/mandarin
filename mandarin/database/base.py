import sqlalchemy.orm
import sqlalchemy_searchable
from sqlalchemy.ext.declarative import declarative_base

Base: declarative_base = declarative_base()
# Initialize search mappers
sqlalchemy_searchable.make_searchable(metadata=Base.metadata)
sqlalchemy.orm.configure_mappers()

__all__ = (
    "Base",
)
