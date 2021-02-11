import royalnet.alchemist as a
import royalnet.typing as t
import sqlalchemy as s
import sqlalchemy.orm as o

from mandarin.database.utils import to_tsvector, gin_index
from .roles import Role
from .songgenres import songgenres
from .songinvolvements import SongInvolvement
from ..base import Base

if t.TYPE_CHECKING:
    from .people import Person
    from .roles import Role


class Song(Base, a.ColRepr, a.Updatable):
    """
    A single song, composed from multiple layers.
    """
    __tablename__ = "songs"

    id = s.Column("id", s.Integer, primary_key=True)

    title = s.Column("title", s.String, nullable=False, default="")
    description = s.Column("description", s.Text, nullable=False, default="")

    disc = s.Column("disc", s.Integer)
    track = s.Column("track", s.Integer)
    year = s.Column("year", s.Integer)
    lyrics = s.Column("lyrics", s.Text, nullable=False, default="")

    album_id = s.Column("album_id", s.Integer, s.ForeignKey("albums.id"))
    album = o.relationship("Album", back_populates="songs")

    layers = o.relationship("Layer", back_populates="song")
    involvements: t.List[SongInvolvement] = o.relationship("SongInvolvement", back_populates="song",
                                                           cascade="all, delete")
    genres = o.relationship("Genre", secondary=songgenres, back_populates="songs")

    # noinspection PyTypeChecker
    search = s.Column("search", to_tsvector(
        a=[title],
        b=[description, year],
        c=[lyrics],
    ))

    __table_args__ = (
        gin_index("songs_gin_index", search),
    )

    def involve(self, people: t.Iterable["Person"], role: "Role") -> t.Set[SongInvolvement]:
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
