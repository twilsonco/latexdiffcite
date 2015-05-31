# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import platform
import itertools
import subprocess

import pytest

from latexdiffcite import latexdiffcite

os.chdir(os.path.dirname(os.path.realpath(__file__)))


def reset_everything():
    latexdiffcite.References.refkeys_old = []
    latexdiffcite.References.refkeys_new = []
    latexdiffcite.References.capture_groups_old = {}
    latexdiffcite.References.capture_groups_new = {}
    latexdiffcite.References.authyear_old = {}
    latexdiffcite.References.authyear_new = {}

    latexdiffcite.Files.out_path = None
    latexdiffcite.Files.tex_old_path = None
    latexdiffcite.Files.tex_new_path = None
    latexdiffcite.Files.bbl_old_path = None
    latexdiffcite.Files.bbl_new_path = None
    latexdiffcite.Files.bib_old_path = []
    latexdiffcite.Files.bib_new_path = []
    latexdiffcite.Files.tex_old_tmp_path = None
    latexdiffcite.Files.tex_old_tmp_hndl = None
    latexdiffcite.Files.tex_new_tmp_path = None
    latexdiffcite.Files.tex_new_tmp_hndl = None

    latexdiffcite.FileContents.tex_old = ''
    latexdiffcite.FileContents.tex_new = ''
    latexdiffcite.FileContents.bib_old = []
    latexdiffcite.FileContents.bib_new = []
    latexdiffcite.FileContents.bbl_old = ''
    latexdiffcite.FileContents.bbl_new = ''

    latexdiffcite.Config.encoding = None
    latexdiffcite.Config.latexdiff_args = None
    latexdiffcite.Config.git_force_unix_pathsep = None
    latexdiffcite.Config.ref_single_word = None
    latexdiffcite.Config.bib = None
    latexdiffcite.Config.bbl = None
    latexdiffcite.Config.cmd_format = None


def mock_git_show(fname, rev):
    '''Replacement for git_show for testing purposes'''
    if platform.system() == 'Windows':
        cmd = 'type'
        shell = True
    else:
        cmd = 'cat'
        shell = False
    p = subprocess.Popen([cmd, fname], stdout=subprocess.PIPE, shell=shell)
    stdout, _ = p.communicate()
    return stdout


parser = latexdiffcite.create_parser()


#==============================================================================
### Outputs
#==============================================================================

out_author_year_agu_bib_non_accented = r'''
\begin{document}
Same-author references are cool [\textit{Foo}, 2010; \textit{Foo and Bar}, 2011a, b, 2012; \textit{Foo et al.}, 2011; \textit{Bar and Baz}, 2013].
citet is pretty awesome too, according to \textit{Foo} [2010] (and later confirmed by \textit{Bar and Baz} [2013]).
Prenote only [e.g. \textit{Foo and Bar}, 2011a].
Pre- and postnote [e.g. \textit{Foo and Bar}, 2011b; \textit{Foo et al.}, 2011, and references therein].
Postnote only [\textit{Foo}, 2010, and references therein].
Testing spaces [pre \textit{Foo and Bar}, 2011a; \textit{Bar and Baz}, 2013, post].
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff [\textit{Foo}, 2010; \textit{Foo et al.}, 2011; \textit{Bar and Baz}, 2013]
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bib_accented = r'''
\begin{document}
Same-author references are cool [\textit{Foo}, 2010; \textit{Föø and Bår}, 2011a, b, 2012; \textit{Foo et al.}, 2011; \textit{Bar and Baz}, 2013].
citet is pretty awesome too, according to \textit{Foo} [2010] (and later confirmed by \textit{Bar and Baz} [2013]).
Prenote only [e.g. \textit{Föø and Bår}, 2011a].
Pre- and postnote [e.g. \textit{Föø and Bår}, 2011b; \textit{Foo et al.}, 2011, and references therein].
Postnote only [\textit{Foo}, 2010, and references therein].
Testing spaces [pre \textit{Föø and Bår}, 2011a; \textit{Bar and Baz}, 2013, post].
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff [\textit{Foo}, 2010; \textit{Foo et al.}, 2011; \textit{Bar and Baz}, 2013]
Accented characters: æÆøØåÅ äÄöÖüÜß
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bib_alt_non_accented = r'''
\newcommand{\ldiffentity}[1]{#1}
\begin{document}
Same-author references are cool (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \textit{Foo and Bar} \ldiffentity{2011a} \ldiffentity{b} \ldiffentity{2012}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}).
citet is pretty awesome too, according to \ldiffentity{\textit{Foo} (\ldiffentity{2010})} (and later confirmed by \ldiffentity{\textit{Bar and Baz} (\ldiffentity{2013})}).
Prenote only (e.g. \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011a}}).
Pre- and postnote (e.g. \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011b}}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}, and references therein).
Postnote only (\ldiffentity{\textit{Foo} \ldiffentity{2010}}, and references therein).
Testing spaces (pre \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011a}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}, post).
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}})
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''
out_author_year_agu_bib_alt_accented = r'''
\newcommand{\ldiffentity}[1]{#1}
\begin{document}
Same-author references are cool (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \textit{Föø and Bår} \ldiffentity{2011a} \ldiffentity{b} \ldiffentity{2012}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}).
citet is pretty awesome too, according to \ldiffentity{\textit{Foo} (\ldiffentity{2010})} (and later confirmed by \ldiffentity{\textit{Bar and Baz} (\ldiffentity{2013})}).
Prenote only (e.g. \ldiffentity{\textit{Föø and Bår} \ldiffentity{2011a}}).
Pre- and postnote (e.g. \ldiffentity{\textit{Föø and Bår} \ldiffentity{2011b}}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}, and references therein).
Postnote only (\ldiffentity{\textit{Foo} \ldiffentity{2010}}, and references therein).
Testing spaces (pre \ldiffentity{\textit{Föø and Bår} \ldiffentity{2011a}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}, post).
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}})
Accented characters: æÆøØåÅ äÄöÖüÜß
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bbl_non_accented = r'''
\begin{document}
Same-author references are cool [\textit{Foo}, 2010; \textit{Foo and Bar}, 2011a, b, 2012; \textit{Foo et~al.}, 2011; \textit{Bar and Baz}, 2013].
citet is pretty awesome too, according to \textit{Foo} [2010] (and later confirmed by \textit{Bar and Baz} [2013]).
Prenote only [e.g. \textit{Foo and Bar}, 2011a].
Pre- and postnote [e.g. \textit{Foo and Bar}, 2011b; \textit{Foo et~al.}, 2011, and references therein].
Postnote only [\textit{Foo}, 2010, and references therein].
Testing spaces [pre \textit{Foo and Bar}, 2011a; \textit{Bar and Baz}, 2013, post].
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff [\textit{Foo}, 2010; \textit{Foo et~al.}, 2011; \textit{Bar and Baz}, 2013]
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bbl_accented = r'''
\begin{document}
Same-author references are cool [\textit{Foo}, 2010; \textit{Föø and Bår}, 2011a, b, 2012; \textit{Foo et~al.}, 2011; \textit{Bar and Baz}, 2013].
citet is pretty awesome too, according to \textit{Foo} [2010] (and later confirmed by \textit{Bar and Baz} [2013]).
Prenote only [e.g. \textit{Föø and Bår}, 2011a].
Pre- and postnote [e.g. \textit{Föø and Bår}, 2011b; \textit{Foo et~al.}, 2011, and references therein].
Postnote only [\textit{Foo}, 2010, and references therein].
Testing spaces [pre \textit{Föø and Bår}, 2011a; \textit{Bar and Baz}, 2013, post].
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff [\textit{Foo}, 2010; \textit{Foo et~al.}, 2011; \textit{Bar and Baz}, 2013]
Accented characters: æÆøØåÅ äÄöÖüÜß
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bbl_alt_non_accented = r'''
\newcommand{\ldiffentity}[1]{#1}
\begin{document}
Same-author references are cool (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \textit{Foo and Bar} \ldiffentity{2011a} \ldiffentity{b} \ldiffentity{2012}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}).
citet is pretty awesome too, according to \ldiffentity{\textit{Foo} (\ldiffentity{2010})} (and later confirmed by \ldiffentity{\textit{Bar and Baz} (\ldiffentity{2013})}).
Prenote only (e.g. \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011a}}).
Pre- and postnote (e.g. \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011b}}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}, and references therein).
Postnote only (\ldiffentity{\textit{Foo} \ldiffentity{2010}}, and references therein).
Testing spaces (pre \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011a}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}, post).
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}})
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bbl_alt_accented = r'''
\newcommand{\ldiffentity}[1]{#1}
\begin{document}
Same-author references are cool (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \textit{Föø and Bår} \ldiffentity{2011a} \ldiffentity{b} \ldiffentity{2012}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}).
citet is pretty awesome too, according to \ldiffentity{\textit{Foo} (\ldiffentity{2010})} (and later confirmed by \ldiffentity{\textit{Bar and Baz} (\ldiffentity{2013})}).
Prenote only (e.g. \ldiffentity{\textit{Föø and Bår} \ldiffentity{2011a}}).
Pre- and postnote (e.g. \ldiffentity{\textit{Föø and Bår} \ldiffentity{2011b}}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}, and references therein).
Postnote only (\ldiffentity{\textit{Foo} \ldiffentity{2010}}, and references therein).
Testing spaces (pre \ldiffentity{\textit{Föø and Bår} \ldiffentity{2011a}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}, post).
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}})
Accented characters: æÆøØåÅ äÄöÖüÜß
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_code_non_accented = r'''
\begin{document}
Same-author references are cool [Foo10, Foo11a, Foo11b, Foo12, Foo11c, Bar13].
citet is pretty awesome too, according to [Foo10] (and later confirmed by [Bar13]).
Prenote only [e.g. Foo11a].
Pre- and postnote [e.g. Foo11b, Foo11c, and references therein].
Postnote only [Foo10, and references therein].
Testing spaces [pre Foo11a, Bar13, post].
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff [Foo10, Foo11c, Bar13]
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_code_accented = r'''
\begin{document}
Same-author references are cool [Foo10, Foo11a, Foo11b, Foo12, Foo11c, Bar13].
citet is pretty awesome too, according to [Foo10] (and later confirmed by [Bar13]).
Prenote only [e.g. Foo11a].
Pre- and postnote [e.g. Foo11b, Foo11c, and references therein].
Postnote only [Foo10, and references therein].
Testing spaces [pre Foo11a, Bar13, post].
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff [Foo10, Foo11c, Bar13]
Accented characters: æÆøØåÅ äÄöÖüÜß
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_numeric_non_accented = r'''
\begin{document}
Same-author references are cool [1, 2, 3, 4, 5, 6].
citet is pretty awesome too, according to [1] (and later confirmed by [6]).
Prenote only [e.g. 2].
Pre- and postnote [e.g. 3, 5, and references therein].
Postnote only [1, and references therein].
Testing spaces [pre 2, 6, post].
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff [1, 5, 6]
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_numeric_accented = r'''
\begin{document}
Same-author references are cool [1, 2, 3, 4, 5, 6].
citet is pretty awesome too, according to [1] (and later confirmed by [6]).
Prenote only [e.g. 2].
Pre- and postnote [e.g. 3, 5, and references therein].
Postnote only [1, and references therein].
Testing spaces [pre 2, 6, post].
Testing commented-out stuff % \cite{notused}
Testing multi-line stuff [1, 5, 6]
Accented characters: æÆøØåÅ äÄöÖüÜß
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

#==============================================================================
### Parametrize a test function
#==============================================================================

# different test cases (citation formatting)
testcases = {
    'author_year_AGU_bib': {
        'template_args_file': 'file -s %FILE% %FILE% -c configs/config_authyear_bib.json',
        'template_args_git': 'git -s %FILE% NOTUSED NOTUSED -c configs/config_authyear_bib.json',
        'out_non_accented': out_author_year_agu_bib_non_accented,
        'out_accented': out_author_year_agu_bib_accented},
    'author_year_AGU_bib_alt': {
        'template_args_file': 'file -s %FILE% %FILE% -c configs/config_authyear_bib_alt.json',
        'template_args_git': 'git -s %FILE% NOTUSED NOTUSED -c configs/config_authyear_bib_alt.json',
        'out_non_accented': out_author_year_agu_bib_alt_non_accented,
        'out_accented': out_author_year_agu_bib_alt_accented},
    'author_year_AGU_bbl': {
        'template_args_file': 'file -s %FILE% %FILE% --bbl bbl_authyear_agu -c configs/config_authyear_bbl.json',
        'template_args_git': 'git -s %FILE% NOTUSED NOTUSED --bbl bbl_authyear_agu -c configs/config_authyear_bbl.json',
        'out_non_accented': out_author_year_agu_bbl_non_accented,
        'out_accented': out_author_year_agu_bbl_accented},
    'author_year_AGU_bbl_alt': {
        'template_args_file': 'file -s %FILE% %FILE% --bbl bbl_authyear_agu -c configs/config_authyear_bbl_alt.json',
        'template_args_git': 'git -s %FILE% NOTUSED NOTUSED --bbl bbl_authyear_agu -c configs/config_authyear_bbl_alt.json',
        'out_non_accented': out_author_year_agu_bbl_alt_non_accented,
        'out_accented': out_author_year_agu_bbl_alt_accented},
    'author_year_code': {
        'template_args_file': 'file -s %FILE% %FILE% --bbl bbl_authyear_code -c configs/config_code.json',
        'template_args_git': 'git -s %FILE% NOTUSED NOTUSED --bbl bbl_authyear_code -c configs/config_code.json',
        'out_non_accented': out_author_year_code_non_accented,
        'out_accented': out_author_year_code_accented},
    'numeric': {
        'template_args_file': 'file -s %FILE% %FILE% -c configs/config_numeric.json',
        'template_args_git': 'git -s %FILE% NOTUSED NOTUSED -c configs/config_numeric.json',
        'out_non_accented': out_numeric_non_accented,
        'out_accented': out_numeric_accented}}

encs = {'non_accented_ANSI': {'enc': 'ascii', 'acc': 'non_accented', 'f_enc': 'ANSI'},
        'accented_ANSI': {'enc': 'iso-8859-1', 'acc': 'accented', 'f_enc': 'ANSI'},
        'accented_UTF8': {'enc': 'utf-8', 'acc': 'accented', 'f_enc': 'UTF8'}}
modes = ['file', 'git']
eols = ['LF', 'CRLF']

parameters = list(itertools.product(testcases.keys(), encs.keys(), modes, eols))
ids = []
for testcase, enc, mode, eol in parameters:
    ids.append('{}_{}_{}_{}'.format(testcase, enc, mode, eol))


class TestFromInputToOutput():

    @pytest.mark.parametrize('testcase, enc, mode, eol', parameters, ids=ids)
    def test_case(self, mocker, testcase, enc, mode, eol):
        mocker.patch('latexdiffcite.latexdiffcite.git_show', side_effect=mock_git_show)
        mocker.patch('latexdiffcite.latexdiffcite.Files.destroy_tempfiles')
        mocker.patch('latexdiffcite.latexdiffcite.run_latexdiff')
        folder = '{}_{}_{}'.format(encs[enc]['acc'], encs[enc]['f_enc'], eol)
        args = testcases[testcase]['template_args_' + mode].replace('%FILE%', os.path.join(folder, 'test.tex')).split()
        parsed_args = parser.parse_args(args)
        latexdiffcite.initiate_from_args(parsed_args)
        latexdiffcite.Config.encoding = encs[enc]['enc']
        parsed_args.func(parsed_args)
        latexdiffcite.Files.tex_old_tmp_hndl.seek(0)
        latexdiffcite.Files.tex_new_tmp_hndl.seek(0)
        out_old = latexdiffcite.Files.tex_old_tmp_hndl.read()
        out_new = latexdiffcite.Files.tex_new_tmp_hndl.read()
        assert out_old == testcases[testcase]['out_' + encs[enc]['acc']]
        assert out_new == testcases[testcase]['out_' + encs[enc]['acc']]

    def setup(self):
        reset_everything()

    def teardown(self):
        latexdiffcite.Files.destroy_tempfiles()


def test_format_authorlist_with_serialcomma(mocker):
    mocker.patch('latexdiffcite.latexdiffcite.Files.destroy_tempfiles')
    latexdiffcite.Config.bib = {
        'max_authors': 0,  # not used
        'sep_authors_first': ', ',
        'author_serialcomma': True,
        'sep_authors_last': ' and ',
        'et_al': 'NOTUSED'
    }
    latexdiffcite.Config.sep_authors_first = ', '
    latexdiffcite.Config.author_serialcomma = True
    latexdiffcite.Config.sep_authors_last = ' and '
    assert latexdiffcite.format_authorlist(['Foo']) == 'Foo'
    assert latexdiffcite.format_authorlist(['Foo', 'Bar']) == 'Foo and Bar'
    assert latexdiffcite.format_authorlist(['Foo', 'Bar', 'Baz']) == 'Foo, Bar, and Baz'


def test_format_authorlist_without_serialcomma(mocker):
    mocker.patch('latexdiffcite.latexdiffcite.Files.destroy_tempfiles')
    latexdiffcite.Config.bib = {
        'max_authors': 0,  # not used
        'sep_authors_first': ', ',
        'author_serialcomma': False,
        'sep_authors_last': ' & ',
        'et_al': 'NOTUSED'
    }
    assert latexdiffcite.format_authorlist(['Foo']) == 'Foo'
    assert latexdiffcite.format_authorlist(['Foo', 'Bar']) == 'Foo & Bar'
    assert latexdiffcite.format_authorlist(['Foo', 'Bar', 'Baz']) == 'Foo, Bar & Baz'


def test_custom_cite_command(mocker):
    mocker.patch('latexdiffcite.latexdiffcite.Files.destroy_tempfiles')
    latexdiffcite.FileContents.tex_new = r'\custom_cite{foo, bar}'
    latexdiffcite.References.refkeys_new = []
    latexdiffcite.Config.cmd_format = {'custom_cite': 'foo'}
    latexdiffcite.get_all_ref_keys('new')
    assert latexdiffcite.References.refkeys_new == ['foo', 'bar']


def test_command_available():
    p = subprocess.Popen(['latexdiffcite', '--version'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    assert 'latexdiffcite version' in str(stdout) or 'latexdiffcite version' in str(stderr)
