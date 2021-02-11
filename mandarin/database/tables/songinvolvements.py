from __future__ import annotations

import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class SongInvolvement(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    The involment of a person in a song.
    """
    __tablename__ = "songinvolvements"

    person_id = s.Column(s.Integer, s.ForeignKey("people.id"), primary_key=True)
    person = o.relationship("Person", back_populates="song_involvements")

    song_id = s.Column(s.Integer, s.ForeignKey("songs.id"), primary_key=True)
    song = o.relationship("Song", back_populates="involvements")

    role_id = s.Column(s.Integer, s.ForeignKey("roles.id"), primary_key=True)
    role = o.relationship("Role", back_populates="song_involvements")

    __table_args__ = (
        """nothing here"""
    )


__all__ = ("SongInvolvement",)
