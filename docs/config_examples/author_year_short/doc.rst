=======================
Author-year short (bbl)
=======================

This configuration outputs references in the form ``[Foo11, Bar13]`` where the last name is abbreviated and joined together with the year. `latexdiffcite` currently has no way of doing that in ``bib`` mode, so this is a configuration for ``bbl`` mode and thus requires that the ``.bbl`` file have more or less the exact format shown below in order to match the regex. Even if your ``.bbl`` file is not exactly like the one here, you might be able to adjust the regex to suit your needs.

**Note:** ``ref_single_word`` is set to ``false`` to keep the example output simple, but it should preferably be set to ``true`` when actually using the example (see :ref:`description_of_settings`).

.. rubric:: ``config.json``

.. literalinclude:: config.json
    :language: json

.. rubric:: ``input.bbl``

.. literalinclude:: input.bbl
    :language: latex

.. rubric:: ``input.tex``

.. literalinclude:: input.tex
    :language: latex

.. rubric:: ``output.tex``

.. literalinclude:: output.tex
    :language: latex
