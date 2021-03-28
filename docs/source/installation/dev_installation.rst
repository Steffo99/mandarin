Install for development
=======================

These are the steps to install Mandarin in development mode.


Clone the repository from GitHub
--------------------------------

The latest development version of Mandarin is always available on
`its GitHub repo <https://github.com/Steffo99/mandarin>`_, on the ``master`` branch.


Having write access
~~~~~~~~~~~~~~~~~~~

If you have write access to the GitHub repository, you can directly **clone** it to your computer with either a
GUI Git client or by entering the following command in the terminal:

.. code-block:: bash

    git clone git@github.com:Steffo99/mandarin.git


Without write access
~~~~~~~~~~~~~~~~~~~~

If you don't have write access to the repository, you'll have to create a **fork** of the project on GitHub.

On the `GitHub repository <https://github.com/Steffo99/mandarin>`_, click the Fork button on the top-right corner,
and then **clone** your new repository with a GUI Git client or with the following terminal command:

.. code-block:: bash

    git clone git@github.com:YOUR-USERNAME-HERE/mandarin.git


Generate the Python environment
-------------------------------

To run Mandarin, you'll need to have a Python environment with all required packages installed.

You can generate one using Poetry by entering the project's directory and running the following terminal command inside:

.. code-block:: bash

    poetry install


Create a configuration file
---------------------------

Before running Mandarin, you'll need to create a ``config.toml`` file from which certain settings will be loaded.

A sample config file is as follows:

.. code-block:: toml

    # OAuth2 authentication parameters
    # If you want to use the demo authentication database, leave them untouched
    # Otherwise, get them from your OAuth2 IDP
    [auth]
    authorization = "https://mandarin.eu.auth0.com/authorize"
    device = "https://mandarin.eu.auth0.com/oauth/device/code"
    token = "https://mandarin.eu.auth0.com/oauth/token"
    refresh = "https://mandarin.eu.auth0.com/oauth/token"
    userinfo = "https://mandarin.eu.auth0.com/userinfo"
    openidcfg = "https://mandarin.eu.auth0.com/.well-known/openid-configuration"
    jwks = "https://mandarin.eu.auth0.com/.well-known/jwks.json"

    # The database uri, in SQLAlchemy format
    # More info here: https://docs.sqlalchemy.org/en/14/core/engines.html
    [database]
    uri = "postgres://mandarin@/mandarin"

    # The broker and backend to use as a task bus, in Celery format
    # More info here: https://docs.celeryproject.org/en/stable/getting-started/brokers/index.html
    [taskbus]
    broker = "redis://localhost"
    backend = "redis://localhost"

    # The directories where data should be stored
    [storage]
    [storage.music]
    dir = "./data/music"
    [storage.tmp]
    dir = "./data/tmp"

    # The TCP ports that the web API should bind itself to
    [apps]
    [apps.debug]
    port = 30009
    [apps.demo]
    port = 30009

    # The names that the roles generated from song ID3 metadata should have
    # Don't change them once if the database already has elements
    [apps.files.roles]
    artist = "Artist"
    composer = "Composer"
    performer = "Performer"

.. important:: Do not use the demo authentication database in a production instance!
