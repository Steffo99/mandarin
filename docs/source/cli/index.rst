Using the CLI tools
=======================

Mandarin supplies a command line interface to perform various actions useful to the management of an instance.

You can access it through the ``mandarin.tools`` Python module:

.. code-block:: bash

    python -m mandarin.tools


Global options
--------------

Debug mode
~~~~~~~~~~

If you want debug output to be printed to stdout, you should append the ``-D`` option:

.. code-block:: bash

    python -m mandarin.tools -D


Specifying an instance
~~~~~~~~~~~~~~~~~~~~~~

To specify the instance you want to operate on, you should append the ``-i {INSTANCE_URL}`` option:

.. code-block:: bash

    python -m mandarin.tools -i "http://127.0.0.1:30009"


Authenticating
~~~~~~~~~~~~~~

To perform actions which require authentication, you must select the ``auth`` subgroup and append the
``--client-id {OAUTH2_CLIENT_ID}`` and ``--audience {OAUTH2_AUDIENCE}``:

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api"


Available commands
------------------

.. toctree::
   :maxdepth: 1

   thesaurus
   upload
   genius
