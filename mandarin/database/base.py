import sqlalchemy_searchable
import sqlalchemy.ext.declarative

Base: sqlalchemy.ext.declarative.declarative_base = sqlalchemy.ext.declarative.declarative_base()
"""
The declarative base for all tables in Mandarin.
"""

sqlalchemy_searchable.make_searchable(metadata=Base.metadata)

__all__ = (
    "Base",
)
