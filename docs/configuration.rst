.. _Configuration:

==================
Configuration file
==================

Default configuration
---------------------

`latexdiffcite` will load settings from three places, each one overriding previous ones:

1. Internal hard-coded defaults (provided below)
2. ``~/.latexdiffcite.json`` (in your user folder) if it exists
3. Settings from a file specified using ``-c CONFIG_FILE``

This way, you can put your preferred settings in ``~/.latexdiffcite.json`` which will be loaded every time, and override them using ``-c CONFIG_FILE`` if necessary.

The configuration file is a JSON file which looks like this:

.. code-block:: json

    {
        "encoding": "utf-8",
        "latexdiff_args": "",
        "git_force_unix_pathsep": true,
        "ref_single_word": true,
        "bib": {
            "max_authors": 2,
            "sep_authors_first": ", ",
            "author_serialcomma": true,
            "sep_authors_last": " and ",
            "et_al": " et~al."
        },
        "bbl": {
            "regex": "\\\\bibitem\\[{((?:(?!^$).)*?)\\(((?:(?!^$).)*?)(?:{\\\\natexlab{(.?)}})?\\)((?:(?!^$).)*?)}\\]{%REFKEY%}",
            "author": "%CG1%",
            "year": "%CG2%%CG3%"
        },
        "cmd_format": {
            "citep": {
                "cite_start": "[",
                "sep_prenote": " ",
                "author": "\\textit{%AUTHOR%}",
                "sep_author_year": ", ",
                "year": "%YEAR%",
                "sep_same_author_year": ", ",
                "sep_ref": "; ",
                "sep_postnote": ", ",
                "cite_end": "]"
            },
            "citet": {
                "cite_start": "",
                "sep_prenote": " ",
                "author": "\\textit{%AUTHOR%}",
                "sep_author_year": " ",
                "year": "[%YEAR%]",
                "sep_same_author_year": ", ",
                "sep_ref": "; ",
                "sep_postnote": ", ",
                "cite_end": ""
            },
            "cite": {
                "cite_start": "",
                "sep_prenote": " ",
                "author": "\\textit{%AUTHOR%}",
                "sep_author_year": " ",
                "year": "[%YEAR%]",
                "sep_same_author_year": ", ",
                "sep_ref": "; ",
                "sep_postnote": ", ",
                "cite_end": ""
            }
        }
    }

Any of the root-level items (``encoding``, ``bib``, ``bbl``, etc.) may be skipped if their defaults work for you (but don't rely on `latexdiffcite`'s defaults to stay consistent across versions).

You can implement support for other citation commands by adding them alongside the existing citation commands.

.. _description_of_settings:

Description of the settings
---------------------------

``encoding``
    The `encoding <https://docs.python.org/3.4/library/codecs.html#standard-encodings>`_ used to read all files (and decode output from ``git show``). Only change this if you experience encoding problems.
``latexdiff_args``
    Extra arguments to pass to `latexdiff`.
``git_force_unix_pathsep``
    Force usage of ``/`` as path separator when extracting files from git. This may be needed when using ``latexdiffcite git`` on Windows.
``ref_single_word``
    If ``true``, each reference will be enclosed in a custom command (``\ldiffentity{}``) that `latexdiff` has no knowledge of. This makes sure each reference is differenced as a whole, instead of `latexdiff` mixing author names and years from old and new references in the diff (might happen if you replace a reference with another). The command definition will be added to the preamble (just before ``\begin{document}``).

``bib``
    Contains settings related to formatting author/year from entries in ``.bib`` files (these settings are only used when running the script without ``--bbl``).

    ``max_authors``
        Maximum number of authors before ``et_al`` is used (see below).
    ``sep_authors_first``
        If more than two authors, this is the separator between all but the last two authors
    ``author_serialcomma``
        If more than two authors, add a comma before the last author (before ``sep_authors_last``, see below).
    ``sep_authors_last``
        This is the separator between the two last (or only) authors.
    ``et_al``
        This will be appended to the author name(s) if there are more than ``max_authors`` authors.

``bbl``
    Contains settings related to parsing ``.bbl`` files (when using the ``--bbl`` option).

    ``regex``
        The `regex <http://www.regular-expressions.info>`_ used to search for a given entry in the ``.bbl`` file. The regex is performed with flags ``ms`` (``.`` matches newlines, and ``^``/``$`` matches start/end of lines). Backslashes must be doubly-escaped. ``%REFKEY%`` is important -- it will be replaced by the reference keys as each one are looked up in turn. The regex typically contains capturing groups, which will be available in some other of the other fields as ``%CG1%``, ``%CG2%``, etc. The script fails if nothing is found, so if you for some reason do not want to capture anything in ``--bbl`` mode, write e.g. ``%REFKEY%`` (which is guaranteed to match). [#tip]_
    ``author``, ``year``
        In order to enable joining together consecutive citations where the author name is the same (e.g., ``Foo et al. (2010, 2011a, b, 2013)`` instead of ``Foo et al. (2010), Foo et al. (2011a), ...``), the script needs to know which of the captured groups are the author and year. Use ``%CG1%``, ``%CG2%`` etc. to specify this in these fields. The author and year is then available as ``%AUTHOR%`` and ``%YEAR%`` in ``cmd_format`` (see below). The first four characters of ``year`` will be compared in order to determine whether to string together identical years (e.g., ``2011a, b`` instead of ``2011a, 2011b``). If you do not wish any of this functionality (for example if your citation style is ``[Foo10, Bar11]``), leave these fields blank. [#sidenote]_

``cmd_format``
    Contains formatting options for all the citation commands. The built-in supported citation commands are ``cite``, ``citet`` and ``citep``. You can implement support for other citation commands by adding them alongside the existing citation commands.

    ``cite_start``
        Put at the start of a citation list.
    ``sep_prenote``
        Separator between prenote and start of references (example: ``citep[e.g.][and references therein]{foo2012}`` becomes ``[e.g. Foo, 2012, and references therein]``).

    ``author``
        Author name(s). Available tokens:

        ``%AUTHOR%``
            Will be replaced by author name for a given reference (e.g. ``Foo``, ``Foo and Bar``, ``Foo et al.``).
        ``%NUMERIC%``
            Will be replaced by the reference number (in order of appearance in the document).
        ``%CG1%``, ``%CG2%``, ...
            Will be replaced by the corresponding capture groups from the regex (only if using ``--bbl`` mode)

    ``sep_author_year``
        Separator between the author and the year.

    ``year``
        Formatting for the reference's year. Available tokens:

        ``%YEAR%``
            Will be replaced by the year (e.g. ``2011``, ``2013a``).
        ``%CG1%``, ``%CG2%``, ...
            Will be replaced by the corresponding capture groups from the regex (only if using ``--bbl`` mode)

    ``sep_same_author_year``
        Separator between years when the author name is the same for consecutive references (the separator between the years in ``[Foo et al., 2012, 2013a, b]``).
    ``sep_ref``
        Separator between references (when consecutive author names are not identical). If the separator is ``'; '``, then ``\citep{foo2012, bar2013}`` might become ``[Foo, 2012; Bar et al., 2013]``.
    ``sep_postnote``
        Separator between end of references and postnote (see ``sep_prenote``).
    ``cite_end``
        Put at the end of a citation list.

.. rubric:: Footnotes

.. [#tip] **Tip:** Use `regex101 <https://regex101.com>`_ to create and check your regex. Paste the contents of your ``.bbl`` file into "test string", and remember to select flavor "python" and flags ``ms``. Use a real reference key for testing, not ``%REFKEY%``. A single reference should be matched, no matter which reference key you put in. The capture groups are displayed to the right. Remember to double all the backslashes when you use the regex in the configuration file.

.. [#sidenote] **Side note:** The default regex matches entries of the form ``\bibitem[{\textit{Foo et al.}(2010)\textit{Foo, Bar and Baz}}]{foo2010}`` or ``\bibitem[{\textit{Foo}(2011{\natexlab{a}})}]{foo2011}``. In the default configuration, ``%AUTHOR%`` would be ``\textit{Foo et al.}`` and ``\textit{Foo}``, while ``%YEAR`` would be ``2010`` and ``2011a``. See the example confiuration files and corresponding ``.bbl`` files for other examples.
