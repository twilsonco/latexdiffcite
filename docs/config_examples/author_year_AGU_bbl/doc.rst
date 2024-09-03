.. _AGU_bbl:

=====================
Author-year AGU (bbl)
=====================

This configuration parses ``.bbl`` files in the style created by the American Geophysical Union's `LaTeX Formatting Toolkit <https://www.latextemplates.com/template/american-geophysical-union>`__ and renders written-out citations the same way BibTeX does using the AGU templates.

The output is exactly the same as :ref:`AGU_bib`.

There are three capture groups:

1. The author string (including ``\textit{}`` and ``et al.``)
2. The year (only the digits)
3. A letter after the year if the year occurs more than once for this author string (empty if there is no letter)

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
