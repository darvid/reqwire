User Guide
==========

.. contents::
   :backlinks: none

Directory Structure
-------------------

Reqwire introduces a **requirements base directory** to the root of your
project, and two subdirectories: a **source** directory and a **build**
directory. By default, the source directory is named *src*, and the
build directory is named *lck* (for lock, as built requirements.txt
files are analogous to the lock files of many other package managers).

The names for all three of these directories are configurable, by
passing the ``-d|--directory``, ``--source-directory``, and
``--build-directory`` options, respectively, to ``reqwire``, **before**
any commands. For example:

.. code-block:: shell

   $ reqwire -d req --source-directory=_src --build-directory=_build build -a
   # ...or...
   $ export REQWIRE_DIR_BASE=req
   $ export REQWIRE_DIR_SOURCE=_src
   $ export REQWIRE_DIR_BUILD=_build
   $ reqwire build -a

Packaging and Version Control
-----------------------------

Ideally, the requirements directory should be located in a project's
root directory, and both source and build directories added to version
control. Depending on the project and target audience, it might make
sense to copy or symlink the primary, built requirements tag (usually
``main``) to a ``requirements.txt`` file in the project root.

If you're distributing a Python package, it might be useful to Include
the *build directory* in your `MANIFEST.in`_ file. This can be simply
achieved with ``graft``::

  graft requirements/lck

Take care to ensure that the built requirements directory is not
ignored by ``.gitignore``, ``.hgignore``, etc. This should not be a
problem if using the default build directory name (*lck*).

.. _MANIFEST.in: https://docs.python.org/3.6/distutils/sourcedist.html#specifying-the-files-to-distribute

Tag Organization
----------------

The purpose of **tags** in reqwire is to provide logical separation of
package requirements based on the environment they target. For instance,
`Sphinx`_ is likely only needed when building documentation, and not at
runtime. `pytest`_ and pytest plugins are only required in a continuous
integration (CI) environment, and so on.

Traditionally, you would use tools like `tox`_, and end up maintaining
requirements in more than one location, and likely not bother to
pin versions or declare sub-dependencies. reqwire makes it convenient
for package maintainers to quickly generate concrete, first-level
requirements, which should hopefully encourage best practices across
all environments.

.. _Sphinx: http://www.sphinx-doc.org/en/1.5.1/
.. _pytest: http://doc.pytest.org/en/latest/
.. _tox: http://tox.readthedocs.io/en/latest/config.html?highlight=deps#confval-deps=MULTI-LINE-LIST

Command Reference
-----------------

reqwire add
~~~~~~~~~~~

* ``reqwire add [specifier]...``

  Installs packages to the local environment and updates one or more
  tagged requirement source files.

  If no other parameters are given, this command will...

  * Resolve the latest version of the provided package(s), unless a
    pinned version is provided.
  * Install the package with **pip**.
  * Add the requirement to the ``main`` tag.

* ``reqwire add -b [specifier]...``

  Calls :ref:`reqwire build` for each tag provided (or ``main`` if no
  tags were provided).

* ``reqwire add [-t <tag name>]... [specifier]...``

  Saves packages to the specified requirement tag(s).

* ``reqwire add --no-install [specifier]...``

  Skips package installation.

* ``reqwire add --no-resolve-canonical-names [specifier]...``

  By default, reqwire will search the Python package index for an exact
  match of package names, and use the canonical name (i.e. casing) for
  each specifier.

  Passing this flag results in the user-provided package being saved to
  requirement source files.

* ``reqwire add --no-resolve-versions [specifier]...``

  By default, reqwire will resolve the latest version for each specifier
  provided.

  Passing this flag allows for adding non-pinned packages to requirement
  source files. In most cases, this is not recommended even though the
  resulting requirement lock files will resolve to latest versions anyway.

* ``reqwire add --pre [specifier]...``

  Includes prerelease versions when resolving versions.

reqwire build
~~~~~~~~~~~~~

* ``reqwire build -a``

  Builds all tags.

* ``reqwire build -t TAG``

  Builds one or more tags.

reqwire init
~~~~~~~~~~~~

* ``reqwire init``

  Scaffolds a requirements directory in the current directory.

* ``reqwire init -f``

  Scaffolds a requirements directory and overwrites any default tag
  names, and ignores pre-existing directories.

* ``reqwire init --index-url=INDEX_URL``

  Changes the base URL written to requirement source files.

* ``reqwire init -t TAG``

  Creates the given tag names as requirement source files.

  If not provided, the tags ``docs``, ``main``, ``qa``, and ``test``
  will get created.

* ``reqwire init --extra-index-url INDEX_URL``

  Adds ``extra-index-url`` options to requirement source files.
