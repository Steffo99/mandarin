import enum


class TimestampOrdering(enum.Enum):
    OLDEST_FIRST = "Oldest-first"
    LATEST_FIRST = "Latest-first"
    ANY = "Any"


__all__ = (
    "TimestampOrdering",
)
