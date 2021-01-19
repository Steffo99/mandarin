# Module docstring
"""
Mass-upload command line tool, to be used when a GUI is not available.
"""

# Special imports
from __future__ import annotations

# External imports
import logging

import click

# Internal imports
# from . import something

# Special global objects
log = logging.getLogger(__name__)


# Code
def validate_url(ctx, param, value):
    """
    Validate the url passed as an argument, possibly checking if a Mandarin instance is running there.

    .. todo:: The validate_url function.
    """
    ...


@click.command()
@click.option(
    "-u", "--base-url",
    required=True,
    type=str,
    callback=validate_url,
    help="The base url of the Mandarin instance you want to upload the files to.",
)
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(exists=True)
)
def upload(base_url, paths):
    """
    .. todo:: The mass-upload tool.
    """


if __name__ == "__main__":
    upload()

# Objects exported by this module
__all__ = (
    "upload",
)
