``thesaurus`` - Genre thesaurus generator
=========================================

The ``thesaurus`` command can be used to quickly populate your database with a hierarchy of many genres.


Specifying the thesaurus file
-----------------------------

To run the ``thesaurus`` command, you have to specify where your thesaurus file is located by passing it as an argument.

.. code-block:: bash

    python -m mandarin.tools \
           -i "http://127.0.0.1:30009" \
           --client-id "OGRdHAUDzny1ioTv8RwcbphzOFOaO6pC" \
           --audience "mandarin-api" \
           thesaurus default_thesaurus.json


Thesaurus file format
~~~~~~~~~~~~~~~~~~~~~

The thesaurus file is a ``.json`` file made of nested objects, where keys are genre names and the objects are the
child genres.

This is an example file we used as a starting point:

.. code-block:: json

    {
        "Metal": {
            "Classic Metal": {},
            "Power Metal": {},
            "Progressive Metal": {}
        },
        "Country": {
            "Alternative Country": {},
            "Americana": {},
            "Cajun": {},
            "Cowboy": {},
            "Texas Country": {},
            "Traditional Country": {}
        },
        "Rock": {
            "Alternative Rock": {},
            "Electronic Rock": {},
            "Experimental Rock": {},
            "Hard Rock": {},
            "Jazz Rock": {},
            "Rock 'n' Roll": {}
        },
        "Pop": {
            "Country Pop": {},
            "C-Pop": {},
            "Dance Pop": {},
            "Electro Pop": {},
            "Europop": {
                "Eurobeat": {},
                "Italo Dance": {},
                "Italo Disco": {},
                "Latin Pop": {}
            },
            "J-Pop": {},
            "K-Pop": {},
            "Lofi": {},
            "Pop Rock": {
                "Power Pop": {},
                "Pop Punk": {
                    "Neon Pop": {},
                    "Emo Pop": {}
                }
            },
            "P-Pop": {}
        },
        "House": {
            "Bass House": {},
            "Deep House": {},
            "Electro House": {},
            "Electro Swing": {},
            "Euro House": {},
            "Hip House": {},
            "Jazz House": {},
            "Tropical House": {},
            "Progressive House": {}
        },
        "Blues": {
            "Blues Rock": {},
            "Electric Blues": {},
            "Punk Blues": {},
            "Soul Blues": {},
            "Gospel Blues": {},
            "Country Blues": {}
        },
        "Hip Hop": {
            "Rap": {},
            "Chap Hop": {},
            "Electro": {},
            "Hardcore Hip Hop": {},
            "Hip Pop": {},
            "Trap": {},
            "Snap": {},
            "Ragga": {},
            "Raggaeton": {}
        },
        "Electronic": {
            "Ambient": {
                "Ambient Dub": {},
                "Dark Ambient": {},
                "New Age": {}
            },
            "Bass Music": {},
            "Disco": {},
            "Drum 'n' Bass": {},
            "Dub": {},
            "Jungle": {},
            "Hardcore": {},
            "Industrial": {},
            "Techno": {},
            "UK Garage": {}
        },
        "Jazz": {
            "Acid Jazz": {},
            "Bebop": {},
            "Cool Jazz": {},
            "Hard Bop": {},
            "Jazz Rap": {},
            "Latin Jazz": {},
            "Punk Jazz": {},
            "Soul Jazz": {}
        },
        "Folk": {
            "Indie Folk": {},
            "Celtic": {},
            "Neofolk": {},
            "Progressive Folk": {},
            "Skiffle": {},
            "Western Music": {}
        },
        "Classical": {
            "Symphony": {},
            "Opera": {},
            "Classical Romantic": {}
        },
        "World": {}
    }
