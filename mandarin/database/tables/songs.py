from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base
from .songgenres import songgenres
from .songinvolvements import SongInvolvement

if TYPE_CHECKING:
    from .people import Person
    from .songroles import SongRole


class Song(Base, a.ColRepr, a.PyModel):
    """
    A single song, composed from multiple layers.
    """
    __tablename__ = "songs"

    id = s.Column(s.Integer, primary_key=True)

    title = s.Column(s.String)

    layers = o.relationship("SongLayer", back_populates="song")

    _album = s.Column(s.Integer, s.ForeignKey("albums.id"))
    album = o.relationship("Album", back_populates="songs")

    involvements = o.relationship("SongInvolvement", back_populates="song")
    genres = o.relationship("MusicGenre", secondary=songgenres, back_populates="songs")

    disc_number = s.Column(s.Integer)
    track_number = s.Column(s.Integer)
    year = s.Column(s.Integer)

    def involve(self, people: Iterable["Person"], role: "SongRole") -> List["SongInvolvement"]:
        """Involve a list of people with this song, and return the resulting involvements."""
        # TODO: should it check for duplicate involvements?

        session = o.session.Session.object_session(self)

        involvements = []

        for person in people:
            involvement = SongInvolvement(song=self, person=person, role=role)
            session.add(involvement)
            involvements.append(involvement)

        return involvements


__all__ = ("Song",)
