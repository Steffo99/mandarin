import pathlib
import royalnet.scrolls

config = royalnet.scrolls.Scroll.from_file("MANDARIN", pathlib.Path("config.toml"), require_file=False)

__all__ = (
    "config",
)
