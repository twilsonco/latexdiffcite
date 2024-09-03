=====
Usage
=====

If properly installed using ``pip install latexdiffcite`` (from PyPI) or ``python setup.py install`` (from source), the script is invoked with ::

    latexdiffcite [args]

If you have simply copied ``latexdiffcite.py`` to somewhere accessible by Python, you need to use ``python -m latexdiffcite [args]`` instead.

`latexdiffcite` has two sub-commands: ``file`` for comparing two files on disk, and ``git`` for comparing two versions of a file in a git repository.

Comparing two files on disk
---------------------------

To compare two files ``FILE_OLD`` and ``FILE_NEW`` on disk::

    latexdiffcite file FILE_OLD FILE_NEW

Comparing revisions of a file in a git repository
-------------------------------------------------

To compare two revisions ``REV_OLD`` and ``REV_NEW`` of a file ``FILE`` in a git repository::

    latexdiffcite git FILE REV_OLD [REV_NEW] [FILE_NEW]

* ``REV_OLD`` and ``REV_NEW`` can be commit hashes, tags, branches, etc.
* ``REV_NEW`` is optional, and defaults to ``HEAD`` (the latest committed version).
* ``FILE_NEW`` is optional, and is used when the new filename/path is different than the old

Optional arguments
------------------

The following optional commands are available:

``-h``, ``--help``
    Show help.
``-c CONFIG_FILE``, ``--config CONFIG_FILE``
    Path to configuration file, see :ref:`Configuration` for details.
``-o FILE_OUT``, ``--output FILE_OUT``
    Output file, default ``diff.tex`` in the current directory.
``-b [BBL_SUBDIR]``, ``--bbl [BBL_SUBDIR]``
    Switches to ``bbl`` mode instead of ``bib`` mode (see :ref:`bib_bbl`). ``BBL_SUBDIR`` (optional) is the path to where the ``.bbl`` file resides relative to the ``.tex`` file (default: same directory as the files). The filename of the ``.bbl`` files are assumed to be the same as the ``.tex`` files (this is not configurable).
``--bbl2 [BBL_NEW_SUBDIR]``
    Use this if the compiled ``.bbl`` file for the new version is in another subdirectory.
``-s``, ``--silent``
    Hide info messages from screen (only show warnings).
``-v``, ``--verbose``
    Show debug log on screen.
``-l [LOGFILE]``, ``--log [LOGFILE]``
    Enable logging to ``LOGFILE`` (default filename: ``latexdiffcite.log``).

.. _bib_bbl:

.bib vs .bbl
------------

`latexdiffcite` is very flexible and can construct the written-out references using either BibTeX ``.bib`` files (default) or the compiled ``.bbl`` files. ``bbl`` mode is activated using the ``-b`` argument.

In ``bib`` mode (default), `latexdiffcite` will look for a ``\bibliography{}`` command in the ``.tex`` files and read the files specified here. Multiple files are supported, but only a single ``\bibliography{}`` command. All the reference keys in the ``.tex`` file will be looked up in the ``.bib`` files, and `latexdiffcite` will create author names and years according to the :ref:`Configuration`. The ``bib`` mode is suited for author-year styles or numeric style.

In ``.bbl`` mode, `latexdiffcite` ignores ``\bibliography{}`` commands and instead reads the compiled ``.bbl`` files. You need to supply a configuration file with a `regular expression <http://www.regular-expressions.info>`_ (regex) used to parse the ``bbl`` file and return capture groups which you can use in the citation formatting. For more details, see :ref:`Configuration` and :ref:`Configuration_Examples`. Note that when you run `latexdiff` in ``git`` mode, the ``.bbl`` file naturally needs to be versioned (and exist in the repository for both revisions).

For both of these modes, `latexdiffcite` will include a ``\nocite{ref1,ref2,...}`` just before ``\end{document}`` containing all the references, so that the bibliography will be rendered as usual.
