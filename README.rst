========================
clickable helper scripts
========================


.. image:: https://img.shields.io/pypi/v/clickable.svg
        :target: https://pypi.python.org/pypi/clickable

.. image:: https://img.shields.io/travis/lalmeras/clickable.svg
        :target: https://travis-ci.org/lalmeras/clickable

.. image:: https://pyup.io/repos/github/lalmeras/clickable/shield.svg
     :target: https://pyup.io/repos/github/lalmeras/clickable/
     :alt: Updates


Helper scripts to write click applications development's environment


* Free software: BSD license


Features
--------

Clickable allows to easily write python and shell-based tools for your projects.

Clickable is based on the following building-blocks:

* a bootstrap.py standalone script that installs a conda based python environment,
  that allows to initialize an isolated python environment.
  (https://github.com/lalmeras/clickable_bootstrap)

* a bootstrap.py's post-install callback that uses poetry to install:

  * your project-related command(s)
  * by python dependencies mechanism, clickable and any optional dependencies

* clickable python library, that provides a clickables.py/clickables.yml file
  loading mechanism

* clickable extensions that provide helpers for writing sphinx, ansible, ...
  commands

Clickable is heavily based on Python, Conda, Poetry and Click projects.


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

