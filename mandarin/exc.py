class MandarinException(Exception):
    """An exception raised by Mandarin."""


class UploadError(MandarinException):
    """An error occoured during the upload of a file."""


class FileAlreadyExistsError(UploadError):
    """
    The file you were trying to upload already exists in the storage.

    (Or there was a SHA512 collision. But the chances of that are astronomically low...)
    """


__all__ = (
    "MandarinException",
    "UploadError",
    "FileAlreadyExistsError",
)
