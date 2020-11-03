from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base
from .albumgenres import albumgenres
from .albuminvolvements import AlbumInvolvement

if TYPE_CHECKING:
    from .people import Person
    from .albumroles import AlbumRole


class Album(Base, a.ColRepr):
    """
    An album, composed of multiple songs.
    """
    __tablename__ = "albums"

    id = s.Column(s.Integer, primary_key=True)
    title = s.Column(s.String, nullable=False)

    involvements = o.relationship("AlbumInvolvement", back_populates="album")

    songs = o.relationship("Song", back_populates="album")
    genres = o.relationship("MusicGenre", secondary=albumgenres, back_populates="albums")

    def involve(self, people: Iterable["Person"], role: "AlbumRole") -> List[AlbumInvolvement]:
        """Involve a list of people with this album, and return the resulting involvements."""
        # TODO: should it check for duplicate involvements?

        session = o.session.Session.object_session(self)

        involvements = []

        for person in people:
            involvement = AlbumInvolvement(album=self, person=person, role=role)
            session.add(involvement)
            involvements.append(involvement)

        return involvements


__all__ = ("Album",)
