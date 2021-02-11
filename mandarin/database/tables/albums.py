import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o
from royalnet.typing import *

from .albumgenres import albumgenres
from .albuminvolvements import AlbumInvolvement
from ..base import Base

if TYPE_CHECKING:
    from .people import Person
    from .roles import Role
    from mandarin.database.utils import to_tsvector

class Album(Base, a.ColRepr, a.Updatable):
    """
    An album, composed of multiple songs.
    """
    __tablename__ = "albums"

    id = s.Column(s.Integer, primary_key=True)
    title = s.Column(s.String, nullable=False, default="")
    description = s.Column(s.Text, nullable=False, default="")

    involvements: List[AlbumInvolvement] = o.relationship("AlbumInvolvement", back_populates="album")
    songs = o.relationship("Song", back_populates="album")
    genres = o.relationship("Genre", secondary=albumgenres, back_populates="albums")

    __table_args__ = (
        to_tsvector(
            a=[title],
            b=[description],
        )
    )

    def involve(self, people: Iterable["Person"], role: "Role") -> List[AlbumInvolvement]:
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
