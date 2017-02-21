============
Contributing
============

Bug reports, feature suggestions and other contributions are greatly appreciated! While I can't promise to implement everything, I will always respond in a timely manner.

Short version
=============

* Submit bug reports and feature requests at `GitHub <https://github.com/cmeeren/latexdiffcite/issues>`__
* Make pull requests to the ``develop`` branch

Bug reports
===========

When `reporting a bug <https://github.com/cmeeren/latexdiffcite/issues>`__ please include:

* your operating system name and version
* any details about your local setup that might be helpful in troubleshooting
* detailed steps to reproduce the bug, which could include:

  * log file (use the ``-l`` option, check that it doesn't contain personal details)
  * the problematic part of your ``.tex`` file, ``.bib`` file and/or ``.bbl`` file

Documentation improvements
==========================

Feel free to add additional configuration examples. This should include, in the style of the existing examples, a minimal working example (no more than the bare minimum to get it working and show how the configuration behaves). You must include:

* the configuration file (include all relevant settings -- don't rely on `latexdiffcite`'s defaults to stay consistent across versions)
* an example ``.bib`` file or ``.bbl`` file
* an example ``.tex`` file
* the output `latexdiffcite` would produce after replacing citation commands

Please run your JSON through a `JSON validator and formatter <http://jsonlint.com>`__ before adding it to the docs.

Feature requests and feedback
=============================

The best way to send feedback is to file an issue at `GitHub <https://github.com/cmeeren/latexdiffcite/issues>`__.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions are welcome :)

Development
===========

To set up `latexdiffcite` for local development:

1. Fork `latexdiffcite` on `GitHub <https://github.com/cmeeren/latexdiffcite/fork>`__.
2. Clone your fork locally::

    git clone git@github.com:your_name_here/latexdiffcite.git

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally. If you add functionality, also add a test in ``tests/test_latexdiffcite.py``. The tests are run with ``py.test`` and can be written as normal functions (starting with ``test_``) containing a standard ``assert`` statement for testing output.

4. When you're done making changes, run all the checks, doc builder and spell checker with `tox <http://tox.readthedocs.io/en/latest/install.html>`__:[1]_ ::

    tox

5. Commit your changes and push your branch to GitHub::

    git add .
    git commit -m "Brief description of your changes."
    git push origin name-of-your-bugfix-or-feature

6. Submit a pull request through the GitHub website. Pull requests should be made to the ``develop`` branch.

Pull Request Guidelines
-----------------------

If you need some code review or feedback while you're developing the code, just make a pull request.

For merging, you should:

1. Write passing tests for new functionality (run ``tox``). [1]_
2. Update/add documentation if relevant.
3. Add yourself to ``AUTHORS.rst``.

.. [1] If you don't have all the necessary python versions available locally you can rely on Travis -- it will
       `run the tests <https://travis-ci.org/cmeeren/latexdiffcite/pull_requests>`__ for each change you add in the pull request. It will be a bit slower than testing locally, though.

Tips
----

To run a subset of tests::

    tox -e envname -- py.test -k test_myfeature

To run all the test environments in parallel (you need to ``pip install detox``)::

    detox
