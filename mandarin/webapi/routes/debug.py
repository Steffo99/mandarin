from __future__ import annotations

import fastapi as f

from . import songs as r_songs
from .. import dependencies
from ...database import create_all, Base, lazy_engine, tables

router_debug = f.APIRouter()


@router_debug.patch(
    "/database/reset",
    summary="Drop and recreate all database tables.",
    status_code=204,
)
def database_reset(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
):
    """
    **Drop** and **recreate** all tables declared using the `DeclarativeBase` in `mandarin.database.base`.

    # THIS DELETES ALL DATA FROM THE DATABASE!
    """
    Base.metadata.drop_all(bind=lazy_engine.evaluate())
    create_all()
    return f.Response(status_code=204)


@router_debug.patch(
    "/songs/genius",
    summary="Fetch data from Genius for all songs in the database.",
    status_code=204,
)
def songs_genius(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
        scrape_title: bool = f.Query(True, description="Whether song titles should be overwritten or not."),
        scrape_description: bool = f.Query(True, description="Whether song descriptions should be overwritten or not."),
        scrape_lyrics: bool = f.Query(False, description="Whether song lyrics should be overwritten or not."),
        scrape_year: bool = f.Query(True, description="Whether song years should be overwritten or not."),
):
    """
    **Replace** the content of all songs with data sourced from Genius with the `lyricsgenius` Python module.

    # THIS IRREVERSIBLY OVERWRITES ALL SONG DATA!
    """
    for song in ls.session.query(tables.Song).all():
        response = r_songs.get_genius(
            ls=ls,
            scrape_title=scrape_title,
            scrape_description=scrape_description,
            scrape_lyrics=scrape_lyrics,
            scrape_year=scrape_year,
            song_id=song.id,
        )
        r_songs.edit_single(
            ls=ls,
            song_id=song.id,
            data=response
        )


__all__ = (
    "router_debug",
)
