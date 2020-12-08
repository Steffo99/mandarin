Requirements
============

Mandarin requires the following software to function properly.


Python 3.8
----------

Mandarin is written in Python, which is an interpreted programming language; therefore, a Python interpreter must be
installed on your system for Mandarin to run.

You can download the latest version of Python from `the official website <https://www.python.org/downloads/>`_, or from
the package manager of your Linux distribution.

.. warning:: As of 2020-12-06, `Debian does not have Python 3.8 in its stable distribution <https://packages.debian.org/search?keywords=python3.8>`_.
             You will need to compile it from source!


Pip
---

Python packages are usually installed through pip, and Mandarin is no exception.

Most Python distributions come with pip preinstalled; to check if it's available, enter the following command in a terminal:

.. code-block:: bash

   pip -V

If it's not available, you probably need to `install it <https://pip.pypa.io/en/stable/installing/>`.


Virtualenv
----------

Usually packaged with Python, virtualenv (or ``venv``) allows to isolate the dependencies of Python scripts from other scripts and the rest of the system.

To check if virtualenv is installed, enter the following command:

.. code-block:: bash

   python -m venv

If it's not available, follow the guide for installing :ref:`Pip`.


PostgreSQL
----------

Mandarin uses a relational database to store song metadata. Thanks to :mod:`sqlalchemy`, it should work with a multitude of
database engines; however, only PostgreSQL is officialy supported.

The used database engine is specified in the config, through either the ``MANDARIN_DATABASE_URI`` environment variable
or the ``database.uri`` key in the ``config.toml`` file.


Hosted locally
~~~~~~~~~~~~~~

You can host an instance of PostgreSQL on the same machine you want to run Mandarin on.

To do so, follow the instructions on `its official website <https://www.postgresql.org/download/>`_.

Once installed, create a new user and database for Mandarin:

.. code-block:: sql

   CREATE USER mandarin_u;
   CREATE DATABASE mandarin_d;

The database URI will then be:

.. code-block::

   postgres://mandarin_u@/mandarin_d


Hosted remotely
~~~~~~~~~~~~~~~

You can use a managed PostgreSQL instance hosted on a different machine by the setting the database URI as follows:

.. code-block::

   postgres://username:password@host/database


Redis
-----

Mandarin uses :mod:`celery` to asyncronously run some tasks.

It requires a interprocess message broker: while `multiple can be used <https://docs.celeryproject.org/en/stable/getting-started/brokers/>`_,
the only one officially supported by Mandarin is Redis.

You can download Redis from `its website <https://redis.io/download>`_ or the package manager of your
Linux distribution.


Poetry
------

Mandarin uses :mod:`poetry` to manage the dependency tree.

If you intend to make dependency-related changes to Mandarin, you'll need to have Poetry installed to be able to update
the ``poetry.lock`` file.

You can download Poetry on its `website <https://python-poetry.org/docs/#installation>`_.


IntelliJ IDEA / PyCharm
-----------------------

Mandarin includes some things that make its development using an IntelliJ IDE a bit more simple.

While **not mandatory**, if you intend to contribute to Mandarin it is suggested that you use either IDEA with the Python plugin or PyCharm.

You can download those from their respective website:
- `PyCharm <https://www.jetbrains.com/pycharm/>`_
- `IDEA <https://www.jetbrains.com/idea/download/>`_

