# Module docstring
"""
This module contains :mod:`celery` tasks which search for a certain element on `Genius <https://genius.com/>`_ using
:mod:`lyricsgenius` and adds the retrieved information to the database.

.. warning:: All information retrieved may be inaccurate, as it is based on the Genius Search.

.. danger::
    Scraping lyrics **violates the terms of service of Genius**, and may or may not be legal in your area.
    Be very careful if you enable lyrics scraping!
"""

# Special imports
from __future__ import annotations

# External imports
import logging

import royalnet.typing as t

from ..__main__ import app as celery
# Internal imports
from ...database import lazy_Session

# Special global objects
log = logging.getLogger(__name__)


# Code
@celery.task
def genius_fetch(table, id_) -> t.Literal[True]:
    session = lazy_Session.evaluate()()
    item = session.query(table).get(id_)
    try:
        item.genius()
    finally:
        session.commit()
        session.close()
    return True


# Objects exported by this module
__all__ = (
    "genius_fetch",
)
