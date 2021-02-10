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

import lyricsgenius
import lyricsgenius.types
import royalnet.lazy as l
import sqlalchemy.orm

from mandarin import exc
# Internal imports
from mandarin.config import lazy_config
from mandarin.database import tables

# Special global objects
log = logging.getLogger(__name__)
lazy_genius = l.Lazy(lambda c: lyricsgenius.Genius(c["genius.token"], verbose=False), c=lazy_config)


# Code
def genius_song(song: tables.Song) -> tables.Song:
    """
    Update the fields of a song with information from Genius.

    :param song: The song to update fields of.
    :return: The same song, allowing for a fluent interface.
    :raises FetchingError: If the song isn't found on Genius.
    """
    genius: lyricsgenius.Genius = lazy_genius.evaluate()
    config = lazy_config.evaluate()
    session: sqlalchemy.orm.Session = sqlalchemy.orm.object_session(song)

    # Find the Artist role
    artist_role = session.query(tables.Role).filter(tables.Role.name == config["apps.files.roles.artist"])

    # Find the artists of the song
    artists = [involvement.person for involvement in song.involvements if involvement.role == artist_role]
    # TODO: For now, just concatenate artists, as they are passed as it is to the Genius Search
    artist = " ".join([artist.name for artist in artists])

    # Search for the song on Genius
    data: lyricsgenius.types.Song = genius.search_song(title=song.title, artist=artist)
    if data is None:
        raise exc.GeniusError("No such song.")

    # Only scrape lyrics if it is enabled in the config
    if config["genius.lyrics"]:
        song.lyrics = data.lyrics

    song.title = data.title
    # TODO: check if this works
    # noinspection PyProtectedMember
    song.description = data._body["description"]["plain"]

    # TODO: should album and artist info be updated too?
    # TODO: are we making a search only for songs, or albums and artists too?

    return song


# Objects exported by this module
__all__ = (
    "genius_song",
)
