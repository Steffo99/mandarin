``upload`` - Bulk uploader
==========================

The ``upload`` command can be used to quickly upload to Mandarin multiple files.

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           upload {FILES...}


Specifying files
----------------

You can specify the files to upload by passing them as arguments of the command:

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           upload mynewsong.mp3 mynewestsong.mp3

To easily upload multiple files, you can employ the variable expansion feature of ``bash``:

.. code-block:: bash

    # Upload all files with the .mp3 extension
    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           upload *.mp3

.. code-block:: bash

    # Upload all files in the current folder, recursively traversing all subdirectories.
    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           upload ./**/*
