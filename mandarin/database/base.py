import sqlalchemy.orm
import sqlalchemy_searchable
from sqlalchemy.ext.declarative import declarative_base

Base: declarative_base = declarative_base()

__all__ = (
    "Base",
)
