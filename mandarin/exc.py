class MandarinException(Exception):
    """An exception raised by Mandarin."""


class UploadError(MandarinException):
    """An error occoured during the upload of a file."""


__all__ = (
    "MandarinException",
    "UploadError",
)
