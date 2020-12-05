import pathlib
import royalnet.scrolls as s
import royalnet.lazy as l


lazy_config = l.Lazy(lambda: s.Scroll.from_file("MANDARIN", pathlib.Path("config.toml")))


__all__ = (
    "lazy_config",
)
