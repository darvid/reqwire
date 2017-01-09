Release Notes
=============

.. contents::
   :backlinks: none

0.1.7 (1/9/2017)
----------------

Bugfix release, thanks to contributions from `ticosax`_.

* Merged `PR #6 <https://github.com/darvid/reqwire/pull/6>`_ by `ticosax`_,
  fixes infinite recursion in
  :meth:`reqwire.helpers.requirements.HashableInstallRequirement.from_line`.

* Merged `PR #8 <https://github.com/darvid/reqwire/pull/8>`_ by `ticosax`_.
  fixes ``--no-resolve-versions``.

* Merged `PR #9 <https://github.com/darvid/reqwire/pull/9>`_ by `ticosax`_,
  removes ``--pin/--no-pin`` flag in favor of ``--no-resolve-versions``.


.. _ticosax: https://github.com/ticosax


0.1.6 (1/7/17)
--------------

* Fixed support for installing/adding editable projects from VCS that
  use `setuptools_scm`_.


.. _setuptools_scm: https://github.com/pypa/setuptools_scm


0.1.5 (1/7/17)
--------------

* Initial support for adding editable requirements.
* Minor bugfixes.
* Added typing as a dependency for Python 2.7 to setup script.


0.1.2 - 0.1.4 (12/23/16)
------------------------

* Various fixes for initialization and Python 2 compatibility.


0.1.1 (12/22/16)
----------------

* Fixed ``reqwire init``, uses user-defined source and build directory
  names.


0.1 (12/22/16)
--------------

* Corrected package setup to include `sh <https://github.com/amoffat/sh>`_
  as an installation dependency.
* Updated ``MANIFEST.in`` to include additional files in distribution.
* Made source and build directories configurable through command-line
  and environment variables.
* File headers now include modelines for Vim and Sublime Text (via
  `STEmacsModelines <https://github.com/kvs/STEmacsModelines>`_).
* Added `reqwire remove` command.

0.1a3 (12/11/16)
----------------

* Adding requirements no longer includes requirements from nested
  requirement files (and possibly constraint files).
* Added initial unit tests.
* Added ``--pre`` option to the **add** command, allowing prerelease
  versions of packages to be installed and added to requirements.
* Added ``-b|--build`` option to the **add** command, which invokes
  the **build** command upon successfully adding packages.
* Added initial documentation.

0.1a2 (12/3/16)
---------------

* Fixed support for Python 2.7.
* Nonexistent requirement directories are now handled gracefully.

0.1a1 (12/1/16)
---------------

* Initial alpha release, includes the **add**, **build**, and **init**
  commands.
