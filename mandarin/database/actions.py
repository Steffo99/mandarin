from . import eng, base, tables
import sqlalchemy.orm
import sqlalchemy_searchable


def create_all() -> None:
    # Create the session
    session = eng.lazy_Session.evaluate()()
    # Initialize search mappers
    sqlalchemy_searchable.make_searchable(metadata=base.Base.metadata)
    sqlalchemy.orm.configure_mappers()
    # Create all tables
    base.Base.metadata.create_all(bind=eng.lazy_engine.evaluate())
    # Create the root genre
    root_genre = session.query(tables.Genre).get(0)
    if root_genre is None:
        # SQLAlchemy type is wrong
        # noinspection PyTypeChecker
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
