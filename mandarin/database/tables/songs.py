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


class Song(Base, a.ColRepr, a.Updatable):
    """
    A single song, composed from multiple layers.
    """
    __tablename__ = "songs"

    id = s.Column(s.Integer, primary_key=True)

    title = s.Column(s.String)

    layers = o.relationship("Layer", back_populates="song")

    _album = s.Column(s.Integer, s.ForeignKey("albums.id"))
    album = o.relationship("Album", back_populates="songs")

    involvements = o.relationship("SongInvolvement", back_populates="song")
    genres = o.relationship("Genre", secondary=songgenres, back_populates="songs")

    disc_number = s.Column(s.Integer)
    track_number = s.Column(s.Integer)
    year = s.Column(s.Integer)

    def involve(self, people: Iterable["Person"], role: "SongRole") -> Set["SongInvolvement"]:
        """
        Involve people with this song, assigning them the specified role, and return all the resulting involvements.

        If the involvement already exists, it won't be created, but it will be returned.
        """

        session = o.session.Session.object_session(self)

        involvements = set()

        for person in people:
            involvement = session.query(SongInvolvement).filter_by(song=self, person=person, role=role).one_or_none()
            if involvement is None:
                involvement = SongInvolvement(song=self, person=person, role=role)
                session.add(involvement)
            involvements.add(involvement)

        return involvements


__all__ = ("Song",)
