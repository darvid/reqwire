Primer
======

.. contents::
   :backlinks: none

Required Reading
----------------

(Pun absolutely intended. 👌)

* Unless you're already familiar with `pip-tools`_, be sure to read
  Vincent Driessen's article on `Better Package Management`_.
* After drinking the `pip-tools`_ kool-aid, read Kenneth Reitz's article
  on `A Better Pip Workflow™`_.
* If by now you're unconvinced that your project could benefit in terms
  of maintainability and build determinism by adding a separate
  requirements.txt for top-level dependencies, then what are you still
  doing here?

State of Python Package Management
----------------------------------

Although `new`__ and `improved`__ ways of managing Python requirements
are on the horizon, the current standard of including and maintaining at
least one requirements.txt file probably isn't going anywhere.

Third-party tools like `pip-tools`_ aren't perfect solutions, but until
an officially sanctioned alternative is implemented and released, Python
package maintainers are going to have to decide the workflow that suits
their needs.

The Case for Tooling
--------------------

Some would argue that installing additional tools to manage package
requirements adds unnecessary overhead to the development process.
This argument certainly has merit, but it should be noted that `pip`_
itself was an external tool until it came installed with Python after
version **2.7.9**. And while Pipfile_ looks incredibly promising, it
might be safe to assume that it wouldn't be included in a Python
distribution in the *immediate* future. Oh, and `virtualenv`_ remains
an external tool, although it was included in the `standard library`__
through `PEP 405`_ (Python 3.3+).

Whether or not extra tooling for managing a project's requirements is
necessary is up to the author(s), but historically, as well as in other
spaces, managing software dependencies has frequently involved more than
one tool.


.. _pip-tools: https://github.com/nvie/pip-tools
.. _Better Package Management: http://nvie.com/posts/better-package-management/
.. _virtual environments: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _A Better Pip Workflow™: https://www.kennethreitz.org/essays/a-better-pip-workflow
.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _Pipfile: https://github.com/pypa/pipfile
.. _pip: https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
.. _venv: https://docs.python.org/3/library/venv.html
.. _PEP 405: https://www.python.org/dev/peps/pep-0405/

__ PEP 518_
__ Pipfile_
__ venv_
