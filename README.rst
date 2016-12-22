reqwire
=======

.. image:: https://img.shields.io/pypi/v/reqwire.svg
   :target: https://pypi.python.org/pypi/reqwire

.. image:: https://img.shields.io/pypi/pyversions/reqwire.svg
   :target: https://pypi.python.org/pypi/reqwire

.. image:: https://travis-ci.org/darvid/reqwire.svg?branch=master
   :target: https://travis-ci.org/darvid/reqwire

.. image:: https://img.shields.io/coveralls/darvid/reqwire.svg
   :target: https://coveralls.io/github/darvid/reqwire

.. image:: https://badges.gitter.im/python-reqwire/Lobby.svg
   :alt: Join the chat at https://gitter.im/python-reqwire/Lobby
   :target: https://gitter.im/python-reqwire/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

**reqwire** wires up your pip requirements with `pip-tools`_.

.. image:: https://asciinema.org/a/97035.png
   :align: center
   :target: https://asciinema.org/a/97035

Install
-------

From **PyPI**::

    $ pip install -U reqwire

From **source**::

    $ pip install -e git+https://github.com/darvid/reqwire.git#egg=reqwire

Features
--------

* Manage multiple requirement source files, or *tags*
* Add requirements from the command line (à la ``npm --save``)
* Compile tagged source files with **pip-compile** (from `pip-tools`_)

Rationale
---------

Until `PEP 518`_ and `Pipfile`_ become reality, maintaining one or more
**requirements.txt** files for Python projects will continue to be
subject to personal preference and differing opinions on best practices
[#]_. Typical workflows involve maintaining multiple
**requirements.txt** files, and many projects have some form of tooling,
be it Makefile targets or external tools, such as Vincent Driessen's
excellent `pip-tools`_.

**reqwire** is a glorified wrapper around pip-tools, and imposes a
slightly opinionated workflow:

* Python requirements are split into *source files* and *built files*,
  with the built files being the output from **pip-compile**, containing
  pinned versions of the entire dependency graph. (Use ``reqwire init``
  to quickly scaffold the necessary directory structure.)
* *Source files* (with the ``.in`` extension) represent a project's
  immediate dependencies, and are always pinned to specific versions or
  version ranges.
* Source filenames are synonymous with *tags*, which can be passed to
  ``reqwire add`` and ``reqwire build`` to maintain requirements for
  entirely separate environments.


Disclaimer
----------

**reqwire** makes no claims about being designed specifically for
humans, bonobos, cats, or any other land mammal. This project is **not**
farm raised, free range, organic, low sugar, MSG free, gluten free,
halal, kosher, vegan, or particularly of any nutritional value
whatsoever. It just wraps `pip-tools`_ and helps you manage your freakin
Python requirements. ☮ 🌈


Links
-----

* `Source code <https://github.com/darvid/reqwire>`_
* `Documentation <http://reqwire.rtfd.io>`_


Roadmap
-------

* Unit tests
* Provide a command to update requirements (user-specified version)
* Provide a command to freshen requirements
* Provide a command to combine tags to a single output file
  (easily possible with **pip-compile**)
* Provide a utility for generating setup and runtime requirements in
  setup.py scripts using setuptools.
* Abandon in favor of `Pipfile`_ 👌


.. _pip-tools: https://github.com/nvie/pip-tools
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _Pipfile: https://github.com/pypa/pipfile

.. [#]

	- http://nvie.com/posts/pin-your-packages/
	- https://www.kennethreitz.org/essays/a-better-pip-workflow
	- https://mail.python.org/pipermail/distutils-sig/2015-December/027954.html
	- https://devcenter.heroku.com/articles/python-pip#best-practices
