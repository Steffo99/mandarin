import lyricsgenius
import lyricsgenius.types
import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o
from royalnet.typing import *

from mandarin import exc
from mandarin.config import lazy_config
from mandarin.genius import lazy_genius
from .roles import Role
from .songgenres import songgenres
from .songinvolvements import SongInvolvement
from ..base import Base

if TYPE_CHECKING:
    from .people import Person
    from .roles import Role



class Song(Base, a.ColRepr, a.Updatable):
    """
    A single song, composed from multiple layers.
    """
    __tablename__ = "songs"

    id = s.Column(s.Integer, primary_key=True)

    title = s.Column(s.String, nullable=False, default="")
    description = s.Column(s.Text, nullable=False, default="")
    lyrics = s.Column(s.Text, nullable=False, default="")

    disc = s.Column(s.Integer)
    track = s.Column(s.Integer)
    year = s.Column(s.Integer)

    album_id = s.Column(s.Integer, s.ForeignKey("albums.id"))
    album = o.relationship("Album", back_populates="songs")

    layers = o.relationship("Layer", back_populates="song")
    involvements: List[SongInvolvement] = o.relationship("SongInvolvement", back_populates="song",
                                                         cascade="all, delete")
    genres = o.relationship("Genre", secondary=songgenres, back_populates="songs")

    def involve(self, people: Iterable["Person"], role: "Role") -> Set[SongInvolvement]:
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

    def genius(self):
        """
        Update the fields of the song with information from Genius.

        :raises FetchingError: If the song isn't found on Genius.
        """
        config = lazy_config.evaluate()
        genius: lyricsgenius.Genius = lazy_genius.evaluate()
        session: o.Session = o.object_session(self)

        # Find the Artist role
        artist_role = session.query(Role).filter(Role.name == config["apps.files.roles.artist"])

        # Find the artists of the song
        artists = [involvement.person for involvement in self.involvements if involvement.role == artist_role]

        # TODO: For now, just concatenate artists, as they are passed as it is to the Genius Search
        artist = " ".join([artist.name for artist in artists])

        # Search for the song on Genius
        data: lyricsgenius.types.Song = genius.search_song(title=self.title, artist=artist)
        if data is None:
            raise exc.GeniusError("No such song.")

        # Only scrape lyrics if it is enabled in the config
        if config["genius.lyrics"]:
            self.lyrics = data.lyrics

        self.title = data.title
        self.description = data.description


__all__ = ("Song",)
