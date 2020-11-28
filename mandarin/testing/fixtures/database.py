import pytest
from mandarin import database


@pytest.fixture
def session():
    """
    Keep a database session open while running the test.
    """
    session = database.Session()
    yield session
    session.close()


@pytest.fixture
def recreate_db():
    """
    Drop and recreate all database tables before running this test.
    """
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)


__all__ = (
    "session",
    "recreate_db",
)
