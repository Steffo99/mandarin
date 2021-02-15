``genius`` - Genius lyrics scraper
==================================

The ``genius`` command uses :mod:`lyricsgenius` to scrape metadata and optionally lyrics for all songs on a Mandarin
instance from `Genius <https://genius.com/>`_.

.. important:: Scraping lyrics is against the Genius Terms of Service and may result in your IP getting blacklisted
               from Genius!


Authenticating with Genius
--------------------------

:mod:`lyricsgenius` requires a Genius API Token to run.

To acquire one, visit the `New API Client <https://genius.com/api-clients/new>`_ page, create a new API Client and then
click on **Generate Access Token**.

The Genius API Token should be passed as the ``-g`` option:

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           genius \
           -g "R03QMjdxjFleMByxvjJ5TONPUv_JrIAG8v5gD4HMZbsnOzuezXOO228c_zmmjKBq"


Specifying the default Artist role name
---------------------------------------

To run properly, the ``genius`` command needs to know which is the default Artist role name of your instance.

If you've changed the default of ``"Artist"``, you'll need to pass the ``--artist-role-name {NAME}`` option.

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           genius \
           -g "R03QMjdxjFleMByxvjJ5TONPUv_JrIAG8v5gD4HMZbsnOzuezXOO228c_zmmjKBq"
           --artist-role-name "Artista"


Automatic mode
--------------------

If you don't want to manually confirm every song update, you can pass the ``--automatic`` option to approve everything
automatically.

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           genius \
           -g "R03QMjdxjFleMByxvjJ5TONPUv_JrIAG8v5gD4HMZbsnOzuezXOO228c_zmmjKBq"
           --automatic

.. warning::

    Please note that the command isn't completely non-interactive: if you haven't logged in, the command will
    still prompt you to complete the device code authentication!


Choosing which fields to scrape
-------------------------------

You can select the fields you want to scrape with the following options:

- ``--scrape-title/--keep-title`` - Song title
- ``--scrape-description/--keep-description`` - Song description
- ``--scrape-lyrics/--keep-lyrics`` - Song lyrics ⚠️
- ``--scrape-year/--keep-year`` - Song release year

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           genius \
           -g "R03QMjdxjFleMByxvjJ5TONPUv_JrIAG8v5gD4HMZbsnOzuezXOO228c_zmmjKBq" \
           --keep-title \
           --scrape-description \
           --scrape-lyrics \
           --scrape-year


Changing the default delay
--------------------------

To prevent getting ratelimited or blacklisted, you may want to increase the delay between two requests: you can do so
with the ``-d {INTERVAL_IN_SECONDS}`` option.

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           genius \
           -g R03QMjdxjFleMByxvjJ5TONPUv_JrIAG8v5gD4HMZbsnOzuezXOO228c_zmmjKBq \
           -d 15.1
