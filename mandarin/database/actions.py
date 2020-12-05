from . import eng, base, tables


def create_all():
    # Create the session
    session = eng.lazy_Session.evaluate()()
    # Create all tables
    base.Base.metadata.create_all(bind=eng.lazy_engine.evaluate())
    # Create the root genre
    root_genre = session.query(tables.Genre).get(0)
    if root_genre is None:
        root_genre = tables.Genre(
            id=0,
            name="Root",
            description="The root genre. All genres are subgenres of this.",
            supergenre_id=None,
        )
        session.add(root_genre)
        session.commit()
    # Close the session
    session.close()


__all__ = (
    "create_all",
)
