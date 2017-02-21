# -*- coding: utf-8 -*-


from __future__ import division, print_function, absolute_import, unicode_literals

import io
import os
import json
import shutil
import itertools
import subprocess

import pytest

from latexdiffcite import latexdiffcite

real_popen = subprocess.Popen
real_json_load = json.load
real_destroy_tempfiles = latexdiffcite.Files.destroy_tempfiles


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

    latexdiffcite.Config.load_defaults()


parser = latexdiffcite.create_parser()


# ==============================================================================
#  Outputs
# ==============================================================================

out_author_year_agu_bib = r'''
\documentclass{article}
\begin{document}
Same-author references are cool [\textit{Foo}, 2010; \textit{Foo and Bar}, 2011a, b, 2012; \textit{Foo et al.}, 2011; \textit{Bar and Baz}, 2013].
citet is pretty awesome too, according to \textit{Foo} [2010] (and later confirmed by \textit{Bar and Baz} [2013]).
Prenote only [e.g. \textit{Foo and Bar}, 2011a].
Pre- and postnote [e.g. \textit{Foo and Bar}, 2011b; \textit{Foo et al.}, 2011, and references therein].
Postnote only [\textit{Foo}, 2010, and references therein].
Testing spaces [pre \textit{Foo and Bar}, 2011a; \textit{Bar and Baz}, 2013, post].
Testing commented-out stuff % \cite{notused}
Testing command inside args [\odot$\dot{T}$ \textit{Foo}, 2010, \odot$\dot{T}$].
Testing multi-line stuff [\textit{Foo}, 2010; \textit{Foo et al.}, 2011; \textit{Bar and Baz}, 2013]
{ACCENTED_CHARACTERS}
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bib_alt = r'''
\documentclass{article}
\newcommand{\ldiffentity}[1]{#1}
\begin{document}
Same-author references are cool (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \textit{Foo and Bar} \ldiffentity{2011a} \ldiffentity{b} \ldiffentity{2012}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}).
citet is pretty awesome too, according to \ldiffentity{\textit{Foo} (\ldiffentity{2010})} (and later confirmed by \ldiffentity{\textit{Bar and Baz} (\ldiffentity{2013})}).
Prenote only (e.g. \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011a}}).
Pre- and postnote (e.g. \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011b}}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}, and references therein).
Postnote only (\ldiffentity{\textit{Foo} \ldiffentity{2010}}, and references therein).
Testing spaces (pre \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011a}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}, post).
Testing commented-out stuff % \cite{notused}
Testing command inside args (\odot$\dot{T}$ \ldiffentity{\textit{Foo} \ldiffentity{2010}}, \odot$\dot{T}$).
Testing multi-line stuff (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \ldiffentity{\textit{Foo, Bar, and Baz} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}})
{ACCENTED_CHARACTERS}
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bbl = r'''
\documentclass{article}
\begin{document}
Same-author references are cool [\textit{Foo}, 2010; \textit{Foo and Bar}, 2011a, b, 2012; \textit{Foo et~al.}, 2011; \textit{Bar and Baz}, 2013].
citet is pretty awesome too, according to \textit{Foo} [2010] (and later confirmed by \textit{Bar and Baz} [2013]).
Prenote only [e.g. \textit{Foo and Bar}, 2011a].
Pre- and postnote [e.g. \textit{Foo and Bar}, 2011b; \textit{Foo et~al.}, 2011, and references therein].
Postnote only [\textit{Foo}, 2010, and references therein].
Testing spaces [pre \textit{Foo and Bar}, 2011a; \textit{Bar and Baz}, 2013, post].
Testing commented-out stuff % \cite{notused}
Testing command inside args [\odot$\dot{T}$ \textit{Foo}, 2010, \odot$\dot{T}$].
Testing multi-line stuff [\textit{Foo}, 2010; \textit{Foo et~al.}, 2011; \textit{Bar and Baz}, 2013]
{ACCENTED_CHARACTERS}
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_agu_bbl_alt = r'''
\documentclass{article}
\newcommand{\ldiffentity}[1]{#1}
\begin{document}
Same-author references are cool (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \textit{Foo and Bar} \ldiffentity{2011a} \ldiffentity{b} \ldiffentity{2012}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}).
citet is pretty awesome too, according to \ldiffentity{\textit{Foo} (\ldiffentity{2010})} (and later confirmed by \ldiffentity{\textit{Bar and Baz} (\ldiffentity{2013})}).
Prenote only (e.g. \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011a}}).
Pre- and postnote (e.g. \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011b}}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}, and references therein).
Postnote only (\ldiffentity{\textit{Foo} \ldiffentity{2010}}, and references therein).
Testing spaces (pre \ldiffentity{\textit{Foo and Bar} \ldiffentity{2011a}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}}, post).
Testing commented-out stuff % \cite{notused}
Testing command inside args (\odot$\dot{T}$ \ldiffentity{\textit{Foo} \ldiffentity{2010}}, \odot$\dot{T}$).
Testing multi-line stuff (\ldiffentity{\textit{Foo} \ldiffentity{2010}}; \ldiffentity{\textit{Foo et~al.} \ldiffentity{2011}}; \ldiffentity{\textit{Bar and Baz} \ldiffentity{2013}})
{ACCENTED_CHARACTERS}
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_author_year_code = r'''
\documentclass{article}
\begin{document}
Same-author references are cool [Foo10, Foo11a, Foo11b, Foo12, Foo11c, Bar13].
citet is pretty awesome too, according to [Foo10] (and later confirmed by [Bar13]).
Prenote only [e.g. Foo11a].
Pre- and postnote [e.g. Foo11b, Foo11c, and references therein].
Postnote only [Foo10, and references therein].
Testing spaces [pre Foo11a, Bar13, post].
Testing commented-out stuff % \cite{notused}
Testing command inside args [\odot$\dot{T}$ Foo10, \odot$\dot{T}$].
Testing multi-line stuff [Foo10, Foo11c, Bar13]
{ACCENTED_CHARACTERS}
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

out_numeric = r'''
\documentclass{article}
\begin{document}
Same-author references are cool [1, 2, 3, 4, 5, 6].
citet is pretty awesome too, according to [1] (and later confirmed by [6]).
Prenote only [e.g. 2].
Pre- and postnote [e.g. 3, 5, and references therein].
Postnote only [1, and references therein].
Testing spaces [pre 2, 6, post].
Testing commented-out stuff % \cite{notused}
Testing command inside args [\odot$\dot{T}$ 1, \odot$\dot{T}$].
Testing multi-line stuff [1, 5, 6]
{ACCENTED_CHARACTERS}
\bibliography{bibl1, bibl2}
\nocite{foo2010,foo2011lorem,foo2011ipsum,foo2012,foo2011dolor,bar2013}
\end{document}
'''

# ==============================================================================
#  Parametrize a test function to test combinations of encodings, styles, etc.
# ==============================================================================


def read_file(fname):
    '''Generic function to read a file'''
    with open(fname, 'r') as f:
        return f.read()


class mock_popen():
    '''Used to mock subprocess.Popen'''

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def communicate(self):
        if self.args[0][0] == 'git':
            # called from git_show
            return real_popen([x.replace('HEAD', '') for x in self.args[0]], **self.kwargs).communicate()
        else:
            # called from run_latexdiff
            return None, None

    def wait(self):
        return 0


def generate_json_load_inject_encoding(enc):

    def json_load_inject_encoding(f):
        d = real_json_load(f)
        d['encoding'] = enc
        return d

    return json_load_inject_encoding


# different test cases (citation formatting)
testcases = {
    'author_year_AGU_bib': {
        'template_args_file': 'file -s %FILE% %FILE% -c tests/configs/config_authyear_bib.json',
        'template_args_git': 'git -s %FILE% HEAD HEAD -c tests/configs/config_authyear_bib.json',
        'out': out_author_year_agu_bib},
    'author_year_AGU_bib_alt': {
        'template_args_file': 'file -s %FILE% %FILE% -c tests/configs/config_authyear_bib_alt.json',
        'template_args_git': 'git -s %FILE% HEAD HEAD -c tests/configs/config_authyear_bib_alt.json',
        'out': out_author_year_agu_bib_alt},
    'author_year_AGU_bbl': {
        'template_args_file': 'file -s %FILE% %FILE% --bbl bbl_authyear_agu -c tests/configs/config_authyear_bbl.json',
        'template_args_git': 'git -s %FILE% HEAD HEAD --bbl bbl_authyear_agu -c tests/configs/config_authyear_bbl.json',
        'out': out_author_year_agu_bbl},
    'author_year_AGU_bbl_alt': {
        'template_args_file': 'file -s %FILE% %FILE% --bbl bbl_authyear_agu -c tests/configs/config_authyear_bbl_alt.json',
        'template_args_git': 'git -s %FILE% HEAD HEAD --bbl bbl_authyear_agu -c tests/configs/config_authyear_bbl_alt.json',
        'out': out_author_year_agu_bbl_alt},
    'author_year_code': {
        'template_args_file': 'file -s %FILE% %FILE% --bbl bbl_authyear_code -c tests/configs/config_code.json',
        'template_args_git': 'git -s %FILE% HEAD HEAD --bbl bbl_authyear_code -c tests/configs/config_code.json',
        'out': out_author_year_code},
    'numeric': {
        'template_args_file': 'file -s %FILE% %FILE% -c tests/configs/config_numeric.json',
        'template_args_git': 'git -s %FILE% HEAD HEAD -c tests/configs/config_numeric.json',
        'out': out_numeric}}

# encoding stuff: what to insert into the output check
encs = {'ascii': '',
        'latin-1': 'æÆøØåÅ äÄöÖüÜß',
        'utf-8': 'æÆøØåÅ äÄöÖüÜß ひらがな'}
# file/git and EOL
modes = ['file', 'git']
eols = ['LF', 'CRLF']

# build all combinations of the above structures
parameters = list(itertools.product(sorted(testcases.keys()), sorted(encs.keys()), modes, eols))
ids = []
for testcase, enc, mode, eol in parameters:
    ids.append('{}_{}_{}_{}'.format(testcase, enc, mode, eol))


class TestHolistic():

    @pytest.mark.parametrize('testcase, enc, mode, eol', parameters, ids=ids)
    def test_case(self, mocker, tmpdir, testcase, enc, mode, eol):
        folder = os.path.join('tests', '{}_{}'.format(enc, eol))
        mocker.patch('latexdiffcite.latexdiffcite.subprocess.Popen', new=mock_popen)
        mocker.patch('latexdiffcite.latexdiffcite.json.load', new=generate_json_load_inject_encoding(enc))
        mocker.patch('latexdiffcite.latexdiffcite.Files.destroy_tempfiles')
        args = testcases[testcase]['template_args_' + mode].replace('%FILE%', os.path.join(folder, 'test.tex')).split()
        args.extend(['-o', str(tmpdir.join('diff.tex'))])
        latexdiffcite.main(args)
        latexdiffcite.Files.tex_old_tmp_hndl.seek(0)
        latexdiffcite.Files.tex_new_tmp_hndl.seek(0)
        out_old = latexdiffcite.Files.tex_old_tmp_hndl.read().decode('utf-8')
        out_new = latexdiffcite.Files.tex_new_tmp_hndl.read().decode('utf-8')
        out_true = testcases[testcase]['out'].replace('{ACCENTED_CHARACTERS}', encs[enc])
        if enc != 'ascii':
            out_true = out_true.replace('Foo and Bar', 'Föø and Bår')
        assert out_old == out_true
        assert out_new == out_true

    def setup(self):
        reset_everything()

    def teardown(self):
        real_destroy_tempfiles()


# ==============================================================================
#  Parametrize a test function to test all examples in the docs
# ==============================================================================


config_examples = os.path.join('docs', 'config_examples')
folders = [x for x in os.listdir(config_examples)
           if os.path.isdir(os.path.join(config_examples, x))]
paths = [os.path.join(config_examples, x) for x in folders]


class TestExamples():

    @pytest.mark.parametrize('folder', paths, ids=folders)
    def test_example(self, mocker, tmpdir, folder):
        mocker.patch('latexdiffcite.latexdiffcite.subprocess.Popen', new=mock_popen)
        mocker.patch('latexdiffcite.latexdiffcite.Files.destroy_tempfiles')
        f_tex = os.path.join(folder, 'input.tex')
        f_cfg = os.path.join(folder, 'config.json')
        f_out = os.path.join(folder, 'output.tex')
        args = ['file', f_tex, f_tex, '-c', f_cfg]
        if 'input.bbl' in os.listdir(folder):
            args.append('--bbl')
        args.extend(['-o', str(tmpdir.join('diff.tex'))])
        parsed_args = parser.parse_args(args)
        latexdiffcite.initiate_from_args(parsed_args)
        latexdiffcite.run(parsed_args)
        latexdiffcite.Files.tex_old_tmp_hndl.seek(0)
        latexdiffcite.Files.tex_new_tmp_hndl.seek(0)
        out_old = latexdiffcite.Files.tex_old_tmp_hndl.read().decode('utf-8')
        out_new = latexdiffcite.Files.tex_new_tmp_hndl.read().decode('utf-8')
        with io.open(f_out, encoding=latexdiffcite.Config.encoding) as f:
            out_answer = f.read()
        assert out_old == out_answer
        assert out_new == out_answer

    def setup(self):
        reset_everything()

    def teardown(self):
        real_destroy_tempfiles()


# ==============================================================================
#  Test specific functions for special cases
# ==============================================================================


class TestIndividualFunctions():

    def setup(self):
        reset_everything()

    def test_format_authorlist_with_serialcomma(self, mocker):
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

    def test_format_authorlist_without_serialcomma(self, mocker):
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

    def test_custom_cite_command(self, mocker):
        latexdiffcite.FileContents.tex_new = r'\custom_cite{foo, bar}'
        latexdiffcite.References.refkeys_new = []
        latexdiffcite.Config.cmd_format = {'custom_cite': 'foo'}
        latexdiffcite.get_all_ref_keys('new')
        assert latexdiffcite.References.refkeys_new == ['foo', 'bar']

    def test_git_force_unix_pathsep(self, mocker):
        '''Test that path separators are correctly handled based on Config.git_force_unix_pathsep'''
        mocked_popen = mocker.patch('latexdiffcite.latexdiffcite.subprocess.Popen')
        mocked_popen.return_value.communicate.return_value = None, None
        mocked_popen.return_value.wait.return_value = 0

        # test that file endings are converted
        latexdiffcite.Config.git_force_unix_pathsep = True
        latexdiffcite.git_show('path\\to\\file.tex', 'HEAD')
        args, kwargs = mocked_popen.call_args
        assert args[0] == ['git', 'show', 'HEAD:path/to/file.tex']

        # test that file endings are not converted
        latexdiffcite.Config.git_force_unix_pathsep = False
        latexdiffcite.git_show('path\\to\\file.tex', 'HEAD')
        args, kwargs = mocked_popen.call_args
        assert args[0] == ['git', 'show', 'HEAD:path\\to\\file.tex']

    def test_git_show_retcode_exception(self, mocker):
        '''Test exception raised when git has nonzero return code'''
        mocked_popen = mocker.patch('latexdiffcite.latexdiffcite.subprocess.Popen')
        mocked_popen.return_value.communicate.return_value = 'stdout', 'stderr'
        mocked_popen.return_value.wait.return_value = 1
        with pytest.raises(ValueError):
            latexdiffcite.git_show('foo', 'bar')

    def test_run_latexdiff_retcode_exception(self, mocker):
        '''Test exception raised when latexdiff has nonzero return code'''
        mocked_popen = mocker.patch('latexdiffcite.latexdiffcite.subprocess.Popen')
        mocked_popen.return_value.communicate.return_value = 'stdout', 'stderr'
        mocked_popen.return_value.wait.return_value = 1
        mocked_popen = mocker.patch('latexdiffcite.latexdiffcite.io.open', autospec=True)
        latexdiffcite.Files.out_path = 'foo'
        with pytest.raises(ValueError):
            latexdiffcite.run_latexdiff('foo', 'bar')

    def test_get_capture_groups_from_bbl_key_not_in_file(self):
        '''Tests exception raised when reference does not exist in the bbl file'''
        latexdiffcite.FileContents.bbl_old = 'foo'
        latexdiffcite.References.refkeys_old = ['bar']
        with pytest.raises(ValueError):
            latexdiffcite.get_capture_groups_from_bbl('old')

    def test_get_capture_groups_from_bbl_wrong_regex(self):
        '''Tests exception raised when reference is not matched in bbl file by the regex'''
        latexdiffcite.Config.bbl['regex'] = r'baz%REFKEY%'
        latexdiffcite.FileContents.bbl_old = 'foo'
        latexdiffcite.References.refkeys_old = ['foo']
        with pytest.raises(ValueError):
            latexdiffcite.get_capture_groups_from_bbl('old')

    def test_find_bibfiles_not_found(self):
        '''Test exception raised when bibfiles are not found'''
        latexdiffcite.Files.tex_old_path = ''
        latexdiffcite.References.refkeys_old = ['foo']
        with pytest.raises(IOError):
            latexdiffcite.find_bibfiles('bibfile', 'old')
        with pytest.raises(IOError):
            latexdiffcite.find_bibfiles('bib1, bib2', 'old')

    def test_make_author_year_tokens_from_bib_no_bibfiles(self):
        '''Tests a path that should never happen, but required to reach 100% test coverage, so why not
        (basically, tests exception raised when searching for refs in bibfiles when there are no bibfiles)'''
        latexdiffcite.References.refkeys_old = ['foo']
        with pytest.raises(ValueError):
            latexdiffcite.make_author_year_tokens_from_bib('old')

    def test_make_author_year_tokens_from_bib_not_found(self):
        '''Tests exception raised when reference does not exist in bib file(s)'''
        latexdiffcite.References.refkeys_old = ['foo']
        latexdiffcite.FileContents.bib_old = ['bar']
        with pytest.raises(ValueError):
            latexdiffcite.make_author_year_tokens_from_bib('old')

    def test_initiate_from_args_bbl2(self):
        '''Tests that --bbl2 optional argument is handled correctly'''
        parsed_args = parser.parse_args(['file', 'foo', 'bar', '--bbl', '--bbl2', 'baz'])

        latexdiffcite.initiate_from_args(parsed_args)
        assert latexdiffcite.Files.bbl_old_path == 'foo.bbl'
        assert latexdiffcite.Files.bbl_new_path == os.path.join('baz', 'bar.bbl')

    def test_main(self, tmpdir, mocker):
        '''Tests the whole shebang, except actually calling latexdiff'''
        mocker.patch('latexdiffcite.latexdiffcite.subprocess.Popen', new=mock_popen)
        fname = os.path.join('tests', 'utf-8_LF', 'test.tex')
        latexdiffcite.main(['file', fname, fname, '-v', '-l', str(tmpdir.join('log.log')),
                            '-o', str(tmpdir.join('diff.tex'))])

# ==============================================================================
#  Subprocess calls: Test invocations
# ==============================================================================


def test_command_available():
    p = subprocess.Popen(['latexdiffcite', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    assert 'latexdiffcite version' in str(stdout) or 'latexdiffcite version' in str(stderr)


def test_run_module():
    p = subprocess.Popen(['python', '-m', 'latexdiffcite', '--version'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    assert 'latexdiffcite version' in str(stdout) or 'latexdiffcite version' in str(stderr)


def test_run_script():
    p = subprocess.Popen(['python', latexdiffcite.__file__, '--version'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    assert 'latexdiffcite version' in str(stdout) or 'latexdiffcite version' in str(stderr)


#-------------------------------------------------------------------------------


@pytest.fixture
def reset(request):
    reset_everything()

    def destroy_tempfiles():
        real_destroy_tempfiles()

    request.addfinalizer(destroy_tempfiles)


def test_home_conf(tmpdir, mocker, reset):
    '''Tests loading of configuration file in user's home directory'''
    def mock_expanduser(path):
        '''Make expanduser expand to temporary directory instead of home directory'''
        return path.replace('~', str(tmpdir))
    mocker.patch('latexdiffcite.latexdiffcite.os.path.expanduser', side_effect=mock_expanduser)
    mocker.patch('latexdiffcite.latexdiffcite.Files.destroy_tempfiles')
    mocker.patch('latexdiffcite.latexdiffcite.run_latexdiff')
    shutil.copy(os.path.join('tests', 'configs', 'config_numeric.json'), os.path.join(str(tmpdir), '.latexdiffcite.json'))
    fname = os.path.join('tests', 'ascii_LF', 'test.tex')
    args = ['file', fname, fname]
    parsed_args = parser.parse_args(args)
    latexdiffcite.initiate_from_args(parsed_args)
    latexdiffcite.run(parsed_args)
    latexdiffcite.Files.tex_old_tmp_hndl.seek(0)
    latexdiffcite.Files.tex_new_tmp_hndl.seek(0)
    out_old = latexdiffcite.Files.tex_old_tmp_hndl.read().decode('utf-8')
    out_new = latexdiffcite.Files.tex_new_tmp_hndl.read().decode('utf-8')
    out_true = out_numeric.replace('{ACCENTED_CHARACTERS}', '')
    assert out_old == out_true
    assert out_new == out_true
