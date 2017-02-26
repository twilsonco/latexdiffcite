# -*- coding: utf-8 -*-


'''latexdiffcite.latexdiffcite: the actual script, and the entry point main()'''


from __future__ import division, print_function, absolute_import, unicode_literals

import io
import os
import re
import json
import logging
import argparse
import tempfile
import subprocess

__version__ = '1.0.6'

log = logging.getLogger(__name__)


# ==============================================================================
#  Classes to hold "global" variables during runtime
# ==============================================================================


class Config(object):

    @staticmethod
    def load_defaults():
        '''Loads default config settings'''
        log.debug('loading default settings')
        Config.encoding = 'utf-8'
        Config.latexdiff_args = ''
        Config.git_force_unix_pathsep = True
        Config.ref_single_word = True
        Config.bib = {
            'max_authors': 2,
            'sep_authors_first': ', ',
            'author_serialcomma': True,
            'sep_authors_last': ' and ',
            'et_al': ' et~al.'
        }
        Config.bbl = {
            'regex': r'\\bibitem\[{((?:(?!^$).)*?)\(((?:(?!^$).)*?)(?:{\\natexlab{(.?)}})?\)((?:(?!^$).)*?)}\]{%REFKEY%}',
            'author': '%CG1%',
            'year': '%CG2%%CG3%'
        }
        Config.cmd_format = {
            'citep':
                {'cite_start': '[',
                 'sep_prenote': ' ',
                 'author': '\\textit{%AUTHOR%}',
                 'sep_author_year': ', ',
                 'year': '%YEAR%',
                 'sep_same_author_year': ', ',
                 'sep_ref': '; ',
                 'sep_postnote': ', ',
                 'cite_end': ']'},
            'citet':
                {'cite_start': '',
                 'sep_prenote': ' ',
                 'author': '\\textit{%AUTHOR%}',
                 'sep_author_year': ' ',
                 'year': '[%YEAR%]',
                 'sep_same_author_year': ', ',
                 'sep_ref': '; ',
                 'sep_postnote': ', ',
                 'cite_end': ''},
            'cite':
                {'cite_start': '',
                 'sep_prenote': ' ',
                 'author': '\\textit{%AUTHOR%}',
                 'sep_author_year': ' ',
                 'year': '[%YEAR%]',
                 'sep_same_author_year': ', ',
                 'sep_ref': '; ',
                 'sep_postnote': ', ',
                 'cite_end': ''}
        }

    @staticmethod
    def load_config(json_file):
        '''Loads settings from config file'''
        with io.open(json_file, 'r', encoding=Config.encoding) as f:
            config = json.load(f)
        for k, v in config.items():
            log.debug('setting Config.%s to %s', k, v)
            setattr(Config, k, v)


class References(object):
    '''Container for reference list and corresponding regex capture groups and author/year strings'''

    refkeys_old = []
    refkeys_new = []
    capture_groups_old = {}
    capture_groups_new = {}
    authyear_old = {}
    authyear_new = {}


class Files(object):
    '''Container for file paths and handles'''

    out_path = None
    tex_old_path = None
    tex_new_path = None
    bbl_old_path = None
    bbl_new_path = None
    bib_old_path = []
    bib_new_path = []

    # temp files
    tex_old_tmp_path = None
    tex_old_tmp_hndl = None
    tex_new_tmp_path = None
    tex_new_tmp_hndl = None

    @staticmethod
    def create_tempfiles():
        '''Create temporary .tex files'''
        for rev in ['new', 'old']:
            tmpfile = tempfile.NamedTemporaryFile(delete=False, prefix='tmp_' + rev + '_', suffix='.tex')
            log.debug('created temp file %s', tmpfile.name)
            setattr(Files, 'tex_' + rev + '_tmp_path', tmpfile.name)
            setattr(Files, 'tex_' + rev + '_tmp_hndl', tmpfile)

    @staticmethod
    def destroy_tempfiles():
        '''Delete temporary .tex files'''
        log.debug('deleting temp file %s', Files.tex_old_tmp_path)
        Files.tex_old_tmp_hndl.close()
        os.remove(Files.tex_old_tmp_path)
        log.debug('deleting temp file %s', Files.tex_new_tmp_path)
        Files.tex_new_tmp_hndl.close()
        os.remove(Files.tex_new_tmp_path)


class FileContents(object):
    '''Container for file contents (multiple bib files supported, so use list of strings instead of single string)'''

    tex_old = ''
    tex_new = ''
    bib_old = []
    bib_new = []
    bbl_old = ''
    bbl_new = ''


# ==============================================================================
#  Functions
# ==============================================================================


def main(args=None):
    '''Entry point for the script'''

    parser = create_parser()
    parsed_args = parser.parse_args(args)
    initiate_from_args(parsed_args)
    run(parsed_args)
    log.info('all done!')


def create_parser():
    '''Creates parser'''
    parser = argparse.ArgumentParser(prog='latexdiffcite',
                                     description='Replaces \\cite{} commands in two files with properly formatted '
                                                 'references and calls latexdiff on the result')

    parser.add_argument('--version', action='version', version='latexdiffcite version {}'.format(__version__))

    # add subparsers: file, git
    subparsers = parser.add_subparsers(title='Subcommands', dest='subcommand',
                                       description='for help, run %(prog)s SUBCOMMAND -h')
    subparsers.required = True
    parser_file = subparsers.add_parser('file', help='compare two files')
    parser_git = subparsers.add_parser('git', help='compare revisions of a file in a git repository')

    # add argument common to all subcommands
    for p in [parser_file, parser_git]:
        p.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='show debug log on screen')
        p.add_argument('-l', '--log', dest='log', metavar='LOGFILE', nargs='?', default=False,
                       const='latexdiffcite.log', help='enable logging to LOGFILE, default %(const)s')
        p.add_argument('-s', '--silent', dest='silent', action='store_true', default=False, help='only show warnings on screen')
        p.add_argument('-o', '--output', dest='file_out', metavar='FILE_OUT',
                       default='diff.tex', help='output file, default %(default)s')
        p.add_argument('-c', '--config', dest='file_config', metavar='CONFIG_FILE',
                       help='config file, see documentation for options')
        p.add_argument('-b', '--bbl', dest='bbl_path', metavar='BBL_SUBDIR', default=None, nargs='?', const='',
                       help='path to where the bbl file resides (default: same directory as file). The filename is '
                            'assumed to be the same as the tex file. The bbl file will be used for formatting '
                            'references instead of getting  author names and year from a bib file. '
                            'Useful e.g. if you are not using author-year style. You will also need to specify a '
                            'configuration file with a regex to extract this info from the bib file, see the '
                            'documentation for details')
        p.add_argument('--bbl2', dest='bbl2_path', metavar='BBL_NEW_SUBDIR', default=None, nargs='?', const='',
                       help='Path to where the new bbl file resides if different from old bbl file.')

    # add positional arguments to file subcommand
    parser_file.add_argument('file_old', metavar='FILE_OLD', help='old revision')
    parser_file.add_argument('file_new', metavar='FILE_NEW', help='new revision')

    # add positional arguments to git subcommand
    parser_git.add_argument('file_old', metavar='FILE', help='file to process (from base of git repository)')
    parser_git.add_argument('rev_old', metavar='REV_OLD', help='commit/tag/branch to use as base')
    parser_git.add_argument('rev_new', metavar='REV_NEW', nargs='?', default='HEAD',
                            help='commit/tag/branch to use as base, default %(default)s')
    parser_git.add_argument('file_new', metavar='FILE_NEW', nargs='?', default=None,
                            help='use if new revision has another filename')

    return parser


def initiate_from_args(args):
    '''Sets up logging and file paths, and loads config'''

    # set up logging
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.NullHandler())
    formatter_full = logging.Formatter('[%(filename)s:%(lineno)4s %(funcName)28s() ] %(levelname)8s  %(message)s')
    formatter_info = logging.Formatter('%(message)s')
    # set up logging to file
    if args.log:
        hdlr_file = logging.FileHandler(args.log, mode='w')
        hdlr_file.setFormatter(formatter_full)
        hdlr_file.setLevel(logging.DEBUG)
        log.addHandler(hdlr_file)
    # set up logging to terminal
    hdlr_stream = logging.StreamHandler()
    if args.verbose:
        hdlr_stream.setLevel(logging.DEBUG)
        hdlr_stream.setFormatter(formatter_full)
    elif not hasattr(args, 'silent') or args.silent:
        hdlr_stream.setLevel(logging.WARNING)
        hdlr_stream.setFormatter(formatter_info)
    else:
        hdlr_stream.setLevel(logging.INFO)
        hdlr_stream.setFormatter(formatter_info)
    log.addHandler(hdlr_stream)

    # paths of tex files
    Files.tex_old_path = args.file_old
    Files.tex_new_path = args.file_new or args.file_old
    log.debug('Old tex path: %s', Files.tex_old_path)
    log.debug('New tex path: %s', Files.tex_new_path)

    # path to bbl files
    if args.bbl2_path is None:
        args.bbl2_path = args.bbl_path
    if args.bbl_path is not None:
        args.bbl_path = os.path.join(os.path.dirname(Files.tex_old_path), args.bbl_path)
        args.bbl2_path = os.path.join(os.path.dirname(Files.tex_new_path), args.bbl2_path)
        bbl_filename = os.path.splitext(os.path.basename(Files.tex_old_path))[0] + '.bbl'
        bbl2_filename = os.path.splitext(os.path.basename(Files.tex_new_path))[0] + '.bbl'
        Files.bbl_old_path = os.path.join(args.bbl_path, bbl_filename)
        Files.bbl_new_path = os.path.join(args.bbl2_path, bbl2_filename)
        log.debug('Old bbl path: %s', Files.bbl_old_path)
        log.debug('New bbl path: %s', Files.bbl_new_path)

    # path to output file
    Files.out_path = args.file_out
    log.debug('Output path: %s', Files.out_path)

    # load config
    Config.load_defaults()
    default_cfile = os.path.expanduser(os.path.join('~', '.latexdiffcite.json'))
    if os.path.isfile(default_cfile):
        log.debug('Loading config from %s', default_cfile)
        Config.load_config(default_cfile)
    if args.file_config:
        log.debug('Loading config from %s', args.file_config)
        Config.load_config(args.file_config)


def run(args):
    '''Replaces references in both revisions and runs latexdiff'''

    if args.subcommand == 'file':
        # read revisions from disk
        read_files('tex')
        if Files.bbl_old_path and Files.bbl_new_path:
            read_files('bbl')
    else:
        # read revisions from git
        log.debug('getting revisions from git')
        git_extract('tex', [args.rev_old, args.rev_new])
        if Files.bbl_old_path and Files.bbl_new_path:
            git_extract('bbl', [args.rev_old, args.rev_new])

    # process the files
    try:
        Files.create_tempfiles()
        process_revision('old')
        process_revision('new')
        run_latexdiff(Files.tex_old_tmp_path, Files.tex_new_tmp_path)
    finally:
        Files.destroy_tempfiles()


def read_files(ext):
    '''Reads the original files'''

    for rev in ['old', 'new']:
        fname = getattr(Files, '{ext}_{rev}_path'.format(ext=ext, rev=rev))
        log.debug('reading %s', fname)
        with io.open(fname, 'r', encoding=Config.encoding) as f:
            setattr(FileContents, '{ext}_{rev}'.format(ext=ext, rev=rev), f.read())


def git_extract(ext, revs):
    '''Extracts revision from git using git show'''

    for oldnew, rev in zip(['old', 'new'], revs):
        fname = getattr(Files, '{ext}_{oldnew}_path'.format(ext=ext, oldnew=oldnew))
        log.debug('running git show %s:%s', rev, fname)
        contents = git_show(fname, rev).decode(Config.encoding).replace('\r\n', '\n')
        setattr(FileContents, '{ext}_{oldnew}'.format(ext=ext, oldnew=oldnew), contents)


def git_show(fname, rev):
    '''Runs git show and returns stdout'''

    # correct path separator
    if Config.git_force_unix_pathsep:
        fname = fname.replace('\\', '/')

    # run git show
    process = subprocess.Popen(['git', 'show', '{}:{}'.format(rev, fname)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    ret_code = process.wait()
    if ret_code:
        raise ValueError('git returned with code {}. Error from git:\n\n'.format(ret_code) + stderr)
    return stdout


def process_revision(oldnew):
    '''Replaces references in revision and writes to temp file'''

    log.info('processing %s revision', oldnew)

    # get references
    log.debug('getting all reference keys from cite commands in %s revision', oldnew)
    get_all_ref_keys(oldnew)

    # get author-year strings and regex capture groups, either from bib file or bbl file
    if getattr(FileContents, 'bbl_' + oldnew):
        # get regex capture groups and make author-year strings from bbl files
        log.debug('retrieving regex matches from bbl')
        get_capture_groups_from_bbl(oldnew)
        make_author_year_tokens_from_bbl(oldnew)
    else:
        # make empty capture group dict
        get_capture_groups_from_bbl(oldnew)
        # make formatted author/year references unless %AUTHOR% and %YEAR% is not present in any formatting
        if any('%AUTHOR%' in fmt['author'] or '%YEAR%' in fmt['year'] for fmt in Config.cmd_format.values()):
            log.debug('creating author/year strings based on bib entries')
            read_bibfile(oldnew)
        else:
            log.debug('%AUTHOR% and %YEAR% tokens not used in format, skipping parsing of bib entries')
        make_author_year_tokens_from_bib(oldnew)

    # replace citations with written-out references
    log.debug('formatting and replacing references in %s revision', oldnew)
    replace_refs_in_tex(oldnew)

    # write contents to temp file
    log.debug('writing %s changes to temp file', oldnew)
    write_tex_to_temp(oldnew)


def get_all_ref_keys(oldnew):
    '''Returns list of all unique reference keys in a revision, in order of appearance'''

    refkeys = []
    s = getattr(FileContents, 'tex_' + oldnew)

    # find arguments of all LaTeX citation commands in document
    all_cite_commands = '|'.join(Config.cmd_format.keys())
    args_all_commands = re.findall(r'\\(?:' + all_cite_commands + r')\s*(?:\[[^\]]*?\]\s*){0,2}\{(.*?)\}', remove_comments(s), flags=re.S)

    # for each citation command, save new references
    for args in args_all_commands:
        ref_list = re.split('\s*,\s*', args)
        log.debug('references found: %s', ref_list)
        new_refs = [r for r in ref_list if r not in refkeys]
        log.debug('new references: %s', new_refs)
        refkeys.extend(new_refs)

    setattr(References, 'refkeys_' + oldnew, refkeys)


def remove_comments(s):
    '''Removes commented-out parts (after %) of lines in a multiline string'''

    s = re.sub(r'%.*', '', s)
    return s


def get_capture_groups_from_bbl(oldnew):
    '''Fetches capture groups from bbl_contents for all refs'''

    refkeys = getattr(References, 'refkeys_' + oldnew)
    bbl_contents = getattr(FileContents, 'bbl_' + oldnew)

    # create empty dict if bbl_contents is empty
    if not bbl_contents:
        setattr(References, 'capture_groups_' + oldnew,
                dict(zip(getattr(References, 'refkeys_' + oldnew), [tuple()]*len(refkeys))))
        return

    capture_groups = {}

    # process each reference individually
    for ref in refkeys:

        # crap out if the reference isn't found in the bbl file
        if ref not in bbl_contents:
            raise ValueError('Reference \'' + ref + '\' not present in bbl file')

        # regex pattern to look for the correct entry
        exp = Config.bbl['regex'].replace('%REFKEY%', ref)
        log.debug('looking for ref %s with regex %s', ref, exp)
        p = re.compile(exp, re.S | re.M)

        # search using the regex, crap out if nothing was matched
        match = re.search(p, bbl_contents)
        if match is None:
            raise ValueError('No match in bbl file for reference ' + ref + ' using regex ' + exp)

        # add captured groups to dict
        capture_groups[ref] = match.groups()

        log.debug('capture tokens from refkey %s: %s', ref, match.groups())

    setattr(References, 'capture_groups_' + oldnew, capture_groups)


def make_author_year_tokens_from_bbl(oldnew):
    '''Fetches the formatted author name and year from bbl_contents'''

    refkeys = getattr(References, 'refkeys_' + oldnew)

    # keys = reference key, values = tuple of (%AUTHOR%, %YEAR%)
    authyear = {}

    # process each reference individually
    for ref in refkeys:

        # get author string from config, replace capture group tokens
        name = Config.bbl['author']
        name = replace_capture_groups(name, ref, oldnew)

        # get year string from config, replace capture group tokens
        year = Config.bbl['year']
        year = replace_capture_groups(year, ref, oldnew)

        # append the name and the year to the list
        authyear[ref] = (name, year)

        log.debug('formatted tokens (%%AUTHOR%%, %%YEAR%%) for %s as %s', ref, (name, year))

    setattr(References, 'authyear_' + oldnew, authyear)


def replace_capture_groups(s, ref, oldnew):
    '''Replaces all capture group tokens in string'''

    for i, replacement in enumerate(getattr(References, 'capture_groups_' + oldnew)[ref]):
        s = s.replace('%CG{}%'.format(i+1), replacement or '')
    return s


def read_bibfile(oldnew):
    '''Reads contents of bibtex files'''

    # get bibtex file
    bibarg = find_bibliography_arg(getattr(FileContents, 'tex_' + oldnew))
    find_bibfiles(bibarg, oldnew)
    bibfiles = getattr(Files, 'bib_' + oldnew + '_path')

    # read bibtex files
    for bibfile in bibfiles:
        log.debug('reading bibtex file %s', bibfile)
        with io.open(bibfile, 'r', encoding=Config.encoding) as f:
            getattr(FileContents, 'bib_' + oldnew).append(f.read())


def find_bibliography_arg(s):
    '''Looks through string for \bibliography{} command and retrieves the argument'''

    log.debug('searching for \\bibliography{} entry in tex file')
    bibfile = re.search(r'$[^%]*\\bibliography\s*{(.*?)}', s, flags=re.M).group(1)
    log.debug('bibliography argument found: %s', bibfile)
    return bibfile


def find_bibfiles(arg, oldnew):
    '''Searches for the bibfiles on the system'''

    sourcepath = os.path.dirname(getattr(Files, 'tex_' + oldnew + '_path'))
    fnames = re.split('\s*,\s*', arg)
    for i, fname in enumerate(fnames):
        fnames[i] = fname if fname.endswith('.bib') else fname + '.bib'

    # check if bibtex file exists (with and without file extension)
    for fname in fnames:
        log.debug('looking for bibtex file "%s" in %s', fname, sourcepath)
        bibpath = os.path.join(sourcepath, fname)
        if not os.path.exists(bibpath):
            raise IOError('bibtex file not found with or without .bib extension: {} ({})'
                          .format(bibpath, os.path.abspath(bibpath)))

        log.debug('found bibtex file %s', os.path.abspath(bibpath))
        getattr(Files, 'bib_' + oldnew + '_path').append(bibpath)


def make_author_year_tokens_from_bib(oldnew):
    '''Looks up reference keys in bib_contents and figures out what the written-out author name and year should be'''

    refkeys = getattr(References, 'refkeys_' + oldnew)

    # if numeric mode (%AUTHOR% and %YEAR% not used in any fields), return empty strings
    if all('%AUTHOR%' not in fmt['author'] and '%YEAR%' not in fmt['year'] for fmt in Config.cmd_format.values()):
        log.debug('no %AUTHOR% or %YEAR% tokens detected in any fields, skipping formatting of author/year')
        authyear = dict(zip(refkeys, [('', '')]*len(refkeys)))
        setattr(References, 'authyear_' + oldnew, authyear)
        return

    # keys = reference key, values = tuple of (%AUTHOR%, %YEAR%)
    authyear = {}

    # process each reference individually
    for ref in refkeys:

        ref_found = False

        # check each bib file
        for i, bib_contents in enumerate(getattr(FileContents, 'bib_' + oldnew)):

            if ref not in bib_contents:
                continue

            log.debug('formatting %s', ref)

            # regex pattern to look for a whole entry - based on tips from the interwebs
            p = re.compile(r'^\s*@\s*\w+\s*\{\s*' + ref + r'\s*,.*?^\}', re.S | re.M)
            entry = re.findall(p, bib_contents)[0]

            # AUTHOR

            # find author list in entry and create author string
            author_re = re.compile(r'author\s*=\s*[{"]((?:[^{}]+?|{[^}]+?})+?)[}"]', re.I | re.M | re.S)

            # split into a list of all authors
            authors = re.split('\s+and\s+', author_re.search(entry).group(1))

            # get a list of only the surnames
            if any(',' in a for a in authors):
                # the name of each author is comma separated
                surnames = [a.split(',')[0] for a in authors]
            else:
                # split on space and assume the last word in each name is the surname
                surnames = [a.split(' ')[-1] for a in authors]

            # remove any curly braces and spaces from surnames
            surnames = [re.sub('[{}]', '', s.strip()) for s in surnames]

            # use "first author et al." if author list is too long
            if len(surnames) > Config.bib['max_authors']:
                name = surnames[0] + Config.bib['et_al']
            else:
                name = format_authorlist(surnames)

            # YEAR

            # find year in entry and create year string
            year_re = re.compile(r'\s*year\s*=\s*["{]?\s*(\d+)\s*["}]?', flags=re.IGNORECASE)
            year = year_re.search(entry).group(1)

            # append the name and the year to the list
            authyear[ref] = (name, year)

            ref_found = True

            log.debug('reference %s found in bibtex file %s', ref, getattr(Files, 'bib_' + oldnew + '_path')[i])
            log.debug('formatted tokens (%%AUTHOR%%, %%YEAR%%) for %s as %s', ref, (name, year))

            # no need to look in other bib files
            break

        # crap out if the reference isn't found in any bib file
        if not ref_found:
            raise ValueError('Reference \'' + ref + '\' not found in any bibtex file')

    setattr(References, 'authyear_' + oldnew, authyear)

    correct_duplicate_authors(oldnew)


def format_authorlist(surnames):
    '''Given a list of surnames, formats a string of all surnames correctly'''

    n = len(surnames)
    serialcomma = ','*(n > 2 and Config.bib['author_serialcomma'])  # serial comma if at least 3 names
    return (('{}' + Config.bib['sep_authors_first'])*(n-2) +  # name + first-kind separator if names > 2
            ('{}' + serialcomma + Config.bib['sep_authors_last'])*(n > 1) +   # penultimate name and last-kind separator
            '{}').format(*surnames)  # final (or only) author name


def correct_duplicate_authors(oldnew):
    '''If the same author string exists for multiple references, appends a letter to the corresponding years,
    e.g. Foo and Bar, 2012a, 2012b (letters will be appended in the order of appearance)'''

    log.debug('looking through author/year for duplicates and appending letter to year')

    authyear = getattr(References, 'authyear_' + oldnew)
    refkeys = getattr(References, 'refkeys_' + oldnew)

    # key = all formatted author/year tuples, values = refkeys where exactly this combo occurs
    occurrences = {}
    for ref in refkeys:
        if authyear[ref] not in occurrences:
            # start a list of occurrences for this author name string
            occurrences[authyear[ref]] = [ref]
        else:
            # the author name string already exists, so we append the current index to the existing list
            occurrences[authyear[ref]].append(ref)

    # now go through each author/year tuple and check if it occurs more than once,
    # and add letters to the years if it does
    for name in occurrences:
        if len(occurrences[name]) > 1:
            # loop through the occurrences of this specific duplicate
            for i in range(len(occurrences[name])):
                # get the reference key where it occurs
                refkey = occurrences[name][i]
                # get the corresponding author and year tuple
                tup = authyear[refkey]
                # add a letter to the year
                year = tup[1] + 'abcdefghijklmnopqrstuvwxyz'[i]
                # replace the tuple in the master list with the new tuple
                log.debug('formatting duplicate %s %s as %s', refkey, authyear[refkey], (tup[0], year))
                authyear[refkey] = (tup[0], year)


def replace_refs_in_tex(oldnew):
    '''The workhorse for replacing LaTeX citation commands with formatted references.

    Searches for citation commands in the tex file contents, calls format_refs() to get the written-out
    citations for each citation command, and replaces the citation command with the written-out citations.'''

    s = getattr(FileContents, 'tex_' + oldnew)

    # find all LaTeX citation commands in the string (exclude commented-out commands)
    matches = re.findall(r'(\\(cite[tp]?)\s*((?:\[[^\]]*?\]\s*){0,2})\{(.*?)\})', remove_comments(s), flags=re.S)

    # process the references for each citation command
    for full_cmd, cite_cmd, opt_args, cite_args in matches:

        log.debug('replacing %s', full_cmd)

        # split args to get a list of reference keys
        refs_this = re.split('\s*,\s*', cite_args)

        # find prenote/postnote if present
        arg1, arg2 = re.search('(?:\[(.*?)\])?\s*(?:\[(.*?)\])?', opt_args).groups()
        if arg2 is None:
            prenote = None
            postnote = arg1
        else:
            prenote = arg1
            postnote = arg2

        # pass the list of references in this command to format_refs() to get the written-out references
        formatted = format_refs(oldnew, refs_this, cite_cmd, prenote, postnote)

        # replace the entire cite command with the written-out references
        s = s.replace(full_cmd, formatted)

    # add \nocite{} before end{document} so that reference list will be written
    nocite = r'\\nocite{' + ','.join(getattr(References, 'refkeys_' + oldnew)) + '}'
    log.debug('adding \\nocite before \\end{document}: %s', nocite)
    s = re.sub(r'(^[^%\n]*?\\end\s*{document})', nocite + r'\n\1', s, flags=re.M)

    # add custom reference protection command to preamble
    if Config.ref_single_word:
        log.debug('adding declaration of citation protection command before \\begin{document}: \\newcommand{\\ldiffentity}[1]{#1}')
        s = re.sub(r'(^[^%\n]*?\\begin\s*{document})', r'\\newcommand{\\ldiffentity}[1]{#1}\n\1', s, flags=re.M)

    setattr(FileContents, 'tex_' + oldnew, s)


def format_refs(oldnew, replace_refs, cite_cmd, prenote, postnote):
    '''The workhorse for creating written-out formatted references corresponding to a given citation command
    and reference list'''

    authyear = getattr(References, 'authyear_' + oldnew)

    # prenotes/postnotes are not implemented for citet, so show a warning if that happens
    if (prenote or postnote) and cite_cmd == 'citet':
        log.warning('postnotes/prenotes are not supported for \\citet{} and will be ignored')
        prenote = None
        postnote = None

    # shortcut to formatting data for this specific cite command
    fmt = Config.cmd_format[cite_cmd]

    # start building the formatted string
    out = fmt['cite_start']

    # add prenote here
    if prenote:
        out += prenote + fmt['sep_prenote']

    # start and end of citation protection command
    ldiffstart = '\\ldiffentity{' if Config.ref_single_word else ''
    ldiffend = '}' if Config.ref_single_word else ''

    # we're going to process each reference by popping them out of the list
    # and looping while there's still something in the list
    while len(replace_refs) > 0:

        ldiff_author = False

        # pop first reference in list
        ref = replace_refs.pop(0)

        # protect each reference with custom command - start the command here unless there are multiple
        # years for this author name
        if len(replace_refs) == 0 or not authyear[replace_refs[0]][0] == authyear[ref][0] != '':
            out += ldiffstart
            ldiff_author = True

        # AUTHOR
        # replace capture groups, %AUTHOR% token and %NUMERIC% token
        author = fmt['author']
        author = replace_capture_groups(author, ref, oldnew)
        author = author.replace('%AUTHOR%', authyear[ref][0])
        author = author.replace('%NUMERIC%', str(getattr(References, 'refkeys_' + oldnew).index(ref)+1))
        out += author

        # author-year separator
        out += fmt['sep_author_year']

        # YEAR
        # replace capture groups
        year = fmt['year']
        year = replace_capture_groups(year, ref, oldnew)

        # To replace the %YEAR% token, a bit more work is required since the year string can consist of
        # multiple years if the author string is the same for consecutive references.
        # First, add the year of the current reference
        year_token = ldiffstart + authyear[ref][1] + ldiffend
        # Continue looping to other references (which are always replace_refs[0] since we're popping) as long as
        # the next ref has same author string as this ref (i.e., no looping if the authors are different),
        # but not if author string is empty
        while len(replace_refs) > 0 and authyear[replace_refs[0]][0] == authyear[ref][0] != '':
            # since we're inside the loop, the next author string is the same,
            # so pop this from the list
            ref2 = replace_refs.pop(0)
            # add the delimiter between years of same author
            year_token += fmt['sep_same_author_year']
            # append the new year  - if the year is the same, only append the letter at the end of the year
            if authyear[ref2][1][0:4] == authyear[ref][1][0:4]:
                year_token += ldiffstart + authyear[ref2][1][4:] + ldiffend
            else:
                year_token += ldiffstart + authyear[ref2][1] + ldiffend

            ref = ref2

        # replace %YEAR% token by the string we made above and append to output
        out += year.replace('%YEAR%', year_token)

        # add the end bracket for reference diff protection
        if ldiff_author:
            out += ldiffend

        # if there are more references, add the separator between citations
        if len(replace_refs) > 0:
            out += fmt['sep_ref']

    # after all references has been added, add postnote
    if postnote:
        out += fmt['sep_postnote'] + postnote

    # finalize and return the result
    out += fmt['cite_end']

    log.debug('result: %s', out)

    return out


def write_tex_to_temp(oldnew):
    '''Writes processed file contents to temp files'''

    log.debug('writing to file %s', getattr(Files, 'tex_' + oldnew + '_tmp_path'))
    fh = getattr(Files, 'tex_' + oldnew + '_tmp_hndl')
    fh.write(getattr(FileContents, 'tex_' + oldnew).encode('utf-8'))
    fh.flush()


def run_latexdiff(file1, file2):
    '''Runs latexdiff on file1 and file2 and writes output to outfile'''

    args = ['latexdiff', file1, file2]
    if Config.latexdiff_args:
        args.append(Config.latexdiff_args)
    log.info('running %s', ' '.join(args))
    log.debug('sending result to %s', Files.out_path)
    with io.open(Files.out_path, 'w', encoding='utf-8') as f:
        process = subprocess.Popen(args, stdout=f, stderr=subprocess.PIPE)
        _, stderr = process.communicate()
        ret_code = process.wait()
        if ret_code:
            raise ValueError('latexdiff returned with code {}. Error from latexdiff:\n\n'.format(ret_code) + stderr)


if __name__ == '__main__':
    # executed if this module is run as a script
    main()
