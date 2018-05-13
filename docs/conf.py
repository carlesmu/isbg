# -*- coding: utf-8 -*-
#
"""Conf file for isbg docs using sphinx."""

# isbg documentation build configuration file, created by
# sphinx-quickstart on Sat Feb 17 12:46:51 2018.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
import re
from ast import literal_eval
import os
import sys
import recommonmark

# -- Custom variables -----------------------------------------------------
cvar_github_base_uri = 'https://github.com/'
cvar_github_prj = 'carlesmu'
cvar_github_usr = 'isbg'
cvar_github_uri = cvar_github_base_uri + cvar_github_prj + '/' + \
    cvar_github_usr
cvar_pypi_uri = 'https://pypi.python.org/pypi/isbg'

master_doc = 'index'  # The master toctree document.

project = u'isbg'
copyright = u'''License GPLv3: GNU GPL version 3 https://gnu.org/licenses/gpl.html

This is free software: you are free to change and redistribute it. There is
NO WARRANTY, to the extent permitted by law.'''

author = u'''This software was mainly written Roger Binns <rogerb@rogerbinns.com> and
maintained by Thomas Lecavelier <thomas@lecavelier.name> since novembre
2009, and maintained by Carles Muñoz Gorriz <carlesmu@internautas.org>
since march 2018.'''

# We get the version from isbg/isbg.py
_VERSION_RE = re.compile(r'__version__\s+=\s+(.*)')
with open('../isbg/isbg.py', 'rb') as f:
    _VERSION = str(literal_eval(_VERSION_RE.search(
        f.read().decode('utf-8')).group(1)))

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
sys.path.insert(0, os.path.abspath('..'))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# -- Extensions -----------------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.doctest',
              'sphinx.ext.intersphinx',
              'sphinx.ext.napoleon',
              'sphinx.ext.coverage',
              'sphinx.ext.mathjax',
              'sphinx.ext.ifconfig',
              'sphinx.ext.extlinks',
              'sphinx.ext.githubpages',
              'sphinx.ext.autosummary',
              'sphinx.ext.todo'
              ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
# source_parsers = {
#    '.md': 'recommonmark.parser.CommonMarkParser',
#}
source_suffix = ['.rst']

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#

# The short X.Y version.
version = _VERSION
# The full version, including alpha/beta/rc tags.
release = _VERSION

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
#exclude_patterns = ['']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for todo extension -------------------------------------------
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for autodoc extension ----------------------------------------
# autoclass_content = 'both'
autodoc_member_order = 'bysource'
autodoc_default_flags = ['members',
                         # 'undoc-members',
                         # 'private-members',
                         # 'special-members',
                         # 'inherited-members',
                         # 'include-private',
                         # 'show-inheritance'
                         ]

autodoc_docstring_signature = False
autodoc_mock_imports = []
autodoc_warningiserror = True

# -- Options for napoleon extension ---------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for extlinks extension ---------------------------------------
extlinks = {
    'issue': (cvar_github_uri + '/issues/%s', 'issue '),  # e.g. :issue:`12`
    'pull': (cvar_github_uri + '/pull/%s', 'pull ')      # e.g. :pull:`11`
}

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
#html_theme = 'alabaster'
#html_theme = 'classic'
#html_theme = 'agogo'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {}

# For theme 'sphinx_rtd_theme':
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    #    'style_external_links': False,
    #    'vcs_pageview_mode': '',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 3,
    #    'includehidden': True,
    #    'titles_only': False
}
# For theme 'alabaster':
"""html_theme_options = {
    #    'logo': logo.png,
    'github_user': cvar_github_usr,
    'github_repo': cvar_github_prj,
    'show_related': True,
    'body_text_align': 'justify',
    'show_powered_by': True,
    'fixed_sidebar': False,
    'github_button': True,
    'travis_button': True,
    'codecov_button': True,
    'gratipay_user': False,
    #    'sidebar_collapse': False,
    'extra_nav_links': {
        u"🚀 Github": cvar_github_uri,
        u"💾 Download Releases": cvar_pypi_uri,
        # u"🖴  Code coverage": "../../htmlcov/index.html",
        # u"📒 API Refence": "api_index.html"
    }
}"""
"""# For theme 'classic':
html_theme_options = {
    "rightsidebar": "true",
    "relbarbgcolor": "black"
}"""

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        # needs 'show_related': True theme option to display:
        'about.html',
        'navigation.html',
        'searchbox.html',
        'relations.html',
    ]
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'isbgdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'isbg.tex', u'isbg Documentation',
     u'author', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('manpage.isbg', 'isbg', u'scans an IMAP Inbox and runs every entry ' +
     u'against SpamAssassin.',
     [author], 1),
    ('manpage.isbg_sa_unwrap', 'isbg_sa_unwrap', u'unwraps a email bundeled ' +
     u'by SpamAssassin.',
     [author], 1),
]
# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'isbg', u'isbg Documentation',
     author, 'isbg', 'One line description of project.',
     'Miscellaneous'),
]

# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}


#
# -- read the docs integration: generate the documentation from sources -----
#

def run_apidoc(_):
    """Run apidoc."""
    try:
        from sphinx.ext.apidoc import main  # sphinx => 1.7.0b1
    except ImportError:
        from sphinx.apidoc import main
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    module = os.path.join(cur_dir, "..", project)
    params = ['-e', '--force', '--separate', '--private', '--follow-links',
              '-o', cur_dir, module]
    main(params)


def import_rsts(_):
    """Copy rst files from base dir to cur dir."""
    import glob
    import shutil
    import os
    import sys
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    for file in glob.glob('../*.rst'):
        shutil.copy2(file, cur_dir)


def import_mds(_):
    """Copy md files from base dir to cur dir."""
    import glob
    import shutil
    import os
    import sys
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    for file in glob.glob('../*.md'):
        shutil.copy2(file, cur_dir)


def setup(app):
    """Configure sphinx."""
    app.connect('builder-inited', run_apidoc)
    app.connect('builder-inited', import_rsts)
