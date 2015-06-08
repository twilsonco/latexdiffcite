| |docs| |version| |downloads| |supported-versions|
| |travis| |appveyor| |codecov| |landscape| |scrutinizer|

.. |docs| image:: https://readthedocs.org/projects/latexdiffcite/badge/?style=flat
    :target: https://readthedocs.org/projects/latexdiffcite
    :alt: Documentation Status

.. |version| image:: http://img.shields.io/pypi/v/latexdiffcite.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/latexdiffcite

.. |downloads| image:: http://img.shields.io/pypi/dm/latexdiffcite.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/latexdiffcite

.. |supported-versions| image:: https://pypip.in/py_versions/latexdiffcite/badge.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/latexdiffcite

.. |travis| image:: http://img.shields.io/travis/cmeeren/latexdiffcite/master.svg?style=flat
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/cmeeren/latexdiffcite

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/cmeeren/latexdiffcite?branch=master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/cmeeren/latexdiffcite

.. |codecov| image:: http://img.shields.io/codecov/c/github/cmeeren/latexdiffcite/master.svg?style=flat
    :alt: Coverage Status
    :target: https://codecov.io/github/cmeeren/latexdiffcite

.. |landscape| image:: https://landscape.io/github/cmeeren/latexdiffcite/master/landscape.svg?style=flat
    :target: https://landscape.io/github/cmeeren/latexdiffcite/master
    :alt: Code Quality Status

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/cmeeren/latexdiffcite/master.svg?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/cmeeren/latexdiffcite/

|

What is `latexdiffcite`?
========================

`latexdiffcite` is a wrapper around `latexdiff` to make citations diff properly:

.. image:: https://latexdiffcite.readthedocs.org/en/latest/_images/illustration.png

`latexdiffcite` is a wrapper around `latexdiff` which, before calling `latexdiff`, replaces (in temporary files!) citation commands such as ``\cite{...}`` with written-out formatted references. It does this by looking up references in a corresponding ``.bib`` file or ``.bbl`` file and formatting them according to a user-specifiable configuration. `latexdiff` will then properly mark changes in the citations. The citation format can be heavily customized to match what you are already getting from LaTeX/BibTeX.


Quick start
===========

`latexdiff` is required, but you of course already have that installed and working, right? :-)

Install with ``pip``::

    pip install latexdiffcite

To compare two ``.tex`` files on disk, use the ``file`` subcommand like this::

    latexdiffcite file FILE_OLD FILE_NEW

To compare two revisions (commit hash, tag, branch, etc.) of a ``.tex`` file in a git repository, use the ``git`` subcommand like this::

    latexdiffcite git FILE REV_OLD [REV_NEW] [FILE_NEW]

* ``REV_OLD`` and ``REV_NEW`` can be commit hashes, tags, branches, etc.
* ``REV_NEW`` is optional, and defaults to ``HEAD`` (the latest committed version).
* ``FILE_NEW`` is optional, and is used when the new filename/path is different than the old


Documentation
=============

For customization and advanced usage, see `latexdiffcite.readthedocs.org <https://latexdiffcite.readthedocs.org/>`_.
