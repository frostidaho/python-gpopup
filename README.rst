========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |
        |
    * - package
      - |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/python-gpopup/badge/?style=flat
    :target: https://readthedocs.org/projects/python-gpopup
    :alt: Documentation Status

.. |version| image:: https://img.shields.io/pypi/v/gpopup.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/gpopup

.. |downloads| image:: https://img.shields.io/pypi/dm/gpopup.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/gpopup

.. |wheel| image:: https://img.shields.io/pypi/wheel/gpopup.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/gpopup

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/gpopup.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/gpopup

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/gpopup.svg?style=flat
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/gpopup


.. end-badges

Popup menu using GTK3

* Free software: BSD license

Installation
============

::

    pip install gpopup

Documentation
=============

https://python-gpopup.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
