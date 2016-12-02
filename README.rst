reqwire
=======

.. image:: https://img.shields.io/pypi/pyversions/reqwire.svg
   :target: https://pypi.python.org/pypi/reqwire

**reqwire** wires up your pip requirements with `pip-tools`_.

.. image:: https://asciinema.org/a/94759.png
   :align: center
   :target: https://asciinema.org/a/94759

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


Roadmap
-------

* Unit tests
* Provide a command to update requirements (user-specified version)
* Provide a command to freshen requirements
* Provide a command to combine tags to a single output file
  (easily possible with **pip-compile**)
* Provide a utility for generating setup and runtime requirements in
  setup.py scripts using setuptools.
* Abandon in favor of Pipfile 👌


.. _pip-tools: https://github.com/nvie/pip-tools
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _Pipfile: https://github.com/pypa/pipfile

.. [#]

	- http://nvie.com/posts/pin-your-packages/
	- https://www.kennethreitz.org/essays/a-better-pip-workflow
	- https://mail.python.org/pipermail/distutils-sig/2015-December/027954.html
	- https://devcenter.heroku.com/articles/python-pip#best-practices
