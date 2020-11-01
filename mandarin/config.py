import pathlib
import royalnet.scrolls

config = royalnet.scrolls.Scroll.from_toml("MANDARIN", pathlib.Path("config.toml"))

__all__ = (
    "config",
)