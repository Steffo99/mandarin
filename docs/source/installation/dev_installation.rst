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


