Quickstart
==========

.. contents::
   :backlinks: none

Installation
------------

**reqwire** supports all versions of Python **above 2.7**. The
recommneded way to install **reqwire** is with pip_:

.. code-block:: shell

   $ pip install reqwire

Source code is available on
`GitHub <https://github.com/darvid/reqwire>`_.

Usage
-----

1. Run ``reqwire init`` in the working directory of your Python project.
   This will scaffold out a requirements directory::

       requirements/
       ├── build
       └── src
           ├── main.in
           ├── qa.in
           └── test.in

2. To add requirements during development, use
   ``reqwire add [-t <tag name>] <requirement>``.

   For example, ``reqwire add -t qa flake8`` will:

   * Resolve the latest version of ``flake8`` (e.g. ``flake8==3.2.1``).
   * Add ``flake8==3.2.1`` to ``requirements/src/qa.in``.

.. _pip: https://pip.pypa.io/en/stable/

3. To compile tags, use ``reqwire build -t <tag name>``.

   To quickly compile *all* tags, use ``reqwire build -a``.
