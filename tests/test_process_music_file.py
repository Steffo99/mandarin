import pytest
import pathlib
import shutil
from mandarin.taskbus.tasks import process_music
from mandarin.database.engine import *
from mandarin.database.base import *
from mandarin.database.tables import *


@pytest.fixture
def sample_noise_path():
    shutil.copy2(pathlib.Path("tests/samples/noise.mp3"), pathlib.Path("tmp/noise.mp3"))
    return "tmp/noise.mp3"


@pytest.fixture
def clean_db():
    """Drop and recreate all database tables before running this test."""
    Base.metadata.drop_all()
    Base.metadata.create_all()


def test_file_processing(clean_db):
    file_id, layer_id = process_music.delay(original_path="tests/samples/noise.mp3").get(timeout=5)

    session = Session()

    file: File = session.query(File).get(file_id)
    assert file is not None
    assert file.name.startswith("data/music/")
    assert file.name.endswith(".mp3")
    assert file.uploader_id is None
    assert file.mime_type == "audio/mpeg"

    layer: Layer = session.query(Layer).get(layer_id)
    assert layer is not None
    assert layer.name == "Default"
    assert layer.description == ""
    assert layer.file_id == file_id
    assert layer.song is None

    session.close()


def test_entries_generation(clean_db):
    _, layer_id = process_music.delay(
        original_path="./tests/samples/noise.mp3",
        generate_entries=True,
    ).get(timeout=5)

    session = Session()

    layer: Layer = session.query(Layer).get(layer_id)
    assert layer.song is not None

    song: Song = layer.song
    assert song.title == "Brownian"
    assert song.disc is None
    assert song.track == 1
    assert song.year == 2020
    assert song.album is not None

    album: Album = song.album
    assert album.title == "Noise"
    assert album.description == ""

    session.close()
