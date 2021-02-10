from __future__ import annotations

import lyricsgenius
import lyricsgenius.types
import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o

from mandarin import exc
from mandarin.config import lazy_config
from mandarin.genius import lazy_genius
from ..base import Base


class Person(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A person who is referenced by at least one song in the catalog.
    """
    __tablename__ = "people"

    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String, nullable=False)
    description = s.Column(s.Text, nullable=False, default="")

    song_involvements = o.relationship("SongInvolvement", back_populates="person", cascade="all, delete")
    album_involvements = o.relationship("AlbumInvolvement", back_populates="person", cascade="all, delete")

    def genius(self):
        """
        Update the fields of the song with information from Genius.

        :raises FetchingError: If the song isn't found on Genius.
        """
        config = lazy_config.evaluate()
        genius: lyricsgenius.Genius = lazy_genius.evaluate()
        session: o.Session = o.object_session(self)

        # Search for the song on Genius
        data: lyricsgenius.types.Artist = genius.search_artist(artist_name=self.name, max_songs=0)
        if data is None:
            raise exc.GeniusError("No such song.")

        self.name = data.name
        self.description = data._body["description"]["plain"]


__all__ = ("Person",)
