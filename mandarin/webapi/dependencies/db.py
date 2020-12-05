from royalnet.typing import *
import logging
import sqlalchemy.orm

from ... import database


log = logging.getLogger(__name__)


def dependency_db_session() -> Iterable[sqlalchemy.orm.session.Session]:
    log.debug("Creating new database session...")
    Session = database.lazy_Session.evaluate()
    session = Session()
    try:
        yield session
    finally:
        log.debug("Closing database session...")
        session.close()


def dependency_db_session_serializable() -> Iterable[sqlalchemy.orm.session.Session]:
    log.debug("Creating new serializable database session...")
    Session: Type[sqlalchemy.orm.Session] = database.lazy_Session.evaluate()
    session: sqlalchemy.orm.Session = Session()
    session.connection(execution_options={"isolation_level": "SERIALIZABLE"})
    try:
        yield session
    finally:
        log.debug("Closing serializable database session...")
        session.close()


__all__ = (
    "dependency_db_session",
    "dependency_db_session_serializable",
)
