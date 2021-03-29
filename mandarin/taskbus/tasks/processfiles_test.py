import pytest
import pathlib
import shutil
import os
import mutagen
import io
import mutagen.mp3
from mandarin.testing.fixtures import *
from mandarin.database import tables

# noinspection PyProtectedMember
from .processfiles import tag_parse, tag_strip, tag_save, tag_process, hash_file, determine_extension, \
    determine_filename, guess_mimetype, find_song_from_tag, find_album_from_tag, make_entries_from_layer, process_music


@pytest.fixture
def tmp_sample_noise_path(tmp_path) -> pathlib.Path:
    """
    Provide a :class:`pathlib.Path` object to a temporary audio file which is unique to each test function.
    """
    src = pathlib.Path("mandarin/testing/samples/noise.mp3")
    dst = tmp_path.joinpath("noise.mp3")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return dst


@pytest.fixture
def tmp_sample_noise_bytesio(tmp_sample_noise_path):
    """
    Provide a :class:`io.BytesIO` object to a temporary audio file which is unique to each test function.
    """
    b = io.BytesIO()
    with open(tmp_sample_noise_path, "rb") as file:
        while data := file.read(8192):
            b.write(data)
    b.seek(0)
    return b


@pytest.fixture
def tmp_sample_noise_mutagen_easy(tmp_sample_noise_bytesio) -> mutagen.File:
    """
    Provide a :class:`mutagen.File` object to a temporary audio file which is unique to each test function.
    """
    return mutagen.File(fileobj=tmp_sample_noise_bytesio, easy=True)


@pytest.fixture
def sample_noise_hash() -> str:
    with open("mandarin/testing/samples/noise.mp3.sha512") as file:
        return file.read()


def test_tag_parse(tmp_sample_noise_mutagen_easy):
    tag = tag_parse(tmp_sample_noise_mutagen_easy)

    assert isinstance(tag, dict)

    assert len(tag["album"]) == 1
    assert tag["album"][0] == "Noise"

    assert len(tag["title"]) == 1
    assert tag["title"][0] == "Brownian"

    assert len(tag["artist"]) == 1
    assert tag["artist"][0] == "Chaos"

    assert len(tag["tracknumber"]) == 1
    assert tag["tracknumber"][0] == "1"

    assert len(tag["genre"]) == 1
    assert tag["genre"][0] == "Random"

    assert len(tag["date"]) == 1
    assert tag["date"][0] == "2020"


def test_tag_strip(tmp_sample_noise_mutagen_easy):
    tag_strip(tmp_sample_noise_mutagen_easy)

    assert tmp_sample_noise_mutagen_easy.tags == {}


def test_tag_save(tmp_sample_noise_bytesio):
    file = mutagen.File(fileobj=tmp_sample_noise_bytesio, easy=True)
    tag_strip(file)
    tag_save(file, tmp_sample_noise_bytesio)
    tmp_sample_noise_bytesio.seek(0)
    new_file = mutagen.mp3.EasyMP3(fileobj=tmp_sample_noise_bytesio)

    assert dict(new_file.tags) == {}


def test_tag_process(tmp_sample_noise_bytesio):
    tag = tag_process(tmp_sample_noise_bytesio)

    assert tag.album.title == "Noise"
    assert tag.song.title == "Brownian"
    assert tag.song.artists[0] == "Chaos"
    assert tag.song.track_number == 1
    assert tag.song.genre == "Random"
    assert tag.song.year == 2020


def test_hash_file(tmp_sample_noise_bytesio, sample_noise_hash):
    h = hash_file(tmp_sample_noise_bytesio)
    assert h.hexdigest() == sample_noise_hash


def test_determine_extension(tmp_sample_noise_path):
    ext = determine_extension(tmp_sample_noise_path)
    assert ext == ".mp3"


def test_guess_mimetype(tmp_sample_noise_path):
    mimetype, mimesoftware = guess_mimetype(tmp_sample_noise_path)
    assert mimetype == "audio/mpeg"
    assert mimesoftware is None


class TestProcessMusic:

    def test_simple(self, recreate_db, session, tmp_sample_noise_bytesio):
        file_id, layer_id = process_music.delay(
            stream=tmp_sample_noise_bytesio,
            original_filename="noise.mp3",
        ).get(timeout=5)
        assert file_id == 1
        assert layer_id == 1

        file: tables.File = session.query(tables.File).get(file_id)
        assert file is not None
        assert file.location.startswith("data/music/")
        assert file.location.endswith(".mp3")
        assert file.uploader_id is None
        assert file.mime_type == "audio/mpeg"

        layer: tables.Layer = session.query(tables.Layer).get(layer_id)
        assert layer is not None
        assert layer.name == "Default"
        assert layer.description == ""
        assert layer.file_id == file_id
        assert layer.song is None

    def test_with_entries(self, recreate_db, session, tmp_sample_noise_bytesio):
        file_id, layer_id = process_music.delay(
            stream=tmp_sample_noise_bytesio,
            original_filename="noise.mp3",
            generate_entries=True,
        ).get(timeout=5)
        assert file_id == 1
        assert layer_id == 1

        layer: tables.Layer = session.query(tables.Layer).get(layer_id)
        assert layer.song is not None

        song: tables.Song = layer.song
        assert song.title == "Brownian"
        assert song.disc is None
        assert song.track == 1
        assert song.year == 2020
        assert song.album is not None

        album: tables.Album = song.album
        assert album.title == "Noise"
        assert album.description == ""
