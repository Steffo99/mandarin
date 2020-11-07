from royalnet.typing import *
import logging
import sqlalchemy.orm

from ...database import *


log = logging.getLogger(__name__)


def dependency_db_session() -> Iterable[sqlalchemy.orm.session.Session]:
    log.debug("Creating new database session...")
    session = Session()
    try:
        yield session
    finally:
        log.debug("Closing database session...")
        session.close()


__all__ = (
    "dependency_db_session",
)
