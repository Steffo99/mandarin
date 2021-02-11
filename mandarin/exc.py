class MandarinException(Exception):
    """An exception raised by Mandarin."""


class UploadError(MandarinException):
    """An error occoured during the upload of a file."""


class ParsingError(MandarinException):
    """An error occoured during the parsing of the tags of a file."""


class GeniusError(MandarinException):
    """An error occoured during the retrieval of extra song information from Genius."""


__all__ = (
    "MandarinException",
    "UploadError",
)
