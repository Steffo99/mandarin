import pytest
import pathlib
from mandarin.taskbus.tasks import process_music


def test_with_no_entries():
    process_music.delay(path="./tests/samples/noise.mp3").get(timeout=5)
