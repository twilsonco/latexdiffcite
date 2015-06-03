=======
Numeric
=======

This configuration outputs references in the form ``[1, 2]``. `latexdiffcite` has built-in support for this by way of the ``%NUMERIC%`` token, which will be replaced by the reference's number (in order of appearance in the document).

**Note:** ``ref_single_word`` is set to ``false`` to keep the example output simple. It has no practical effect in this style, since each reference is just a single number.

.. rubric:: ``config.json``

.. literalinclude:: config.json
    :language: json

.. rubric:: ``input.tex``

.. literalinclude:: input.tex
    :language: latex

.. rubric:: ``output.tex``

.. literalinclude:: output.tex
    :language: latex
