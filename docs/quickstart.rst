===========
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

For customization of the citation format, see :ref:`Configuration` and :ref:`Configuration_Examples`.
