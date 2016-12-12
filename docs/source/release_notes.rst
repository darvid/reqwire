Release Notes
=============

.. contents::
   :backlinks: none

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
