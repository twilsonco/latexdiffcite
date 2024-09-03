.. _AGU_bib:

=====================
Author-year AGU (bib)
=====================

This configuration parses ``.bib`` files and creates written-out citations in the same style BibTeX does using the American Geophysical Union's `LaTeX Formatting Toolkit <https://www.latextemplates.com/template/american-geophysical-union>`__.

The output is exactly the same as :ref:`AGU_bbl`.

**Note:** ``ref_single_word`` is set to ``false`` to keep the example output simple, but it should preferably be set to ``true`` when actually using the example (see :ref:`description_of_settings`).

.. rubric:: ``config.json``

.. literalinclude:: config.json
    :language: json

.. rubric:: ``input.bib``

.. literalinclude:: input.bib
    :language: latex

.. rubric:: ``input.tex``

.. literalinclude:: input.tex
    :language: latex

.. rubric:: ``output.tex``

.. literalinclude:: output.tex
    :language: latex
