import lyricsgenius
import royalnet.lazy

from .config import lazy_config

lazy_genius = royalnet.lazy.Lazy(lambda c: lyricsgenius.Genius(c["genius.token"], verbose=False), c=lazy_config)

__all__ = (
    "lazy_genius",
)
