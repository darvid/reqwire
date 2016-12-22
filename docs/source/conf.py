# -*- coding: utf-8 -*-
import pkg_resources


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinxcontrib.napoleon',
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'reqwire'
copyright = u'2016, David Gidwani'
author = u'David Gidwani'
version = pkg_resources.get_distribution('reqwire').version
release = version
language = None
exclude_patterns = []
pygments_style = 'sphinx'
todo_include_todos = True
html_theme = 'material_design'
html_theme_options = {
    'pygments_theme': 'lovelace',
    'ribbon_bg': 'ribbon-slava-bowman.jpg',
    # 'ribbon_bg_size': 'auto auto',
    'ribbon_bg_position': 'left 60%',
}
html_static_path = ['_static']
htmlhelp_basename = 'reqwiredoc'
latex_documents = [
    (master_doc, 'reqwire.tex', u'reqwire Documentation',
     u'David Gidwani', 'manual'),
]
man_pages = [
    (master_doc, 'reqwire', u'reqwire Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'reqwire', u'reqwire Documentation',
     author, 'reqwire', 'Wire up Python requirements with pip-tools.',
     'Miscellaneous'),
]
intersphinx_mapping = {
    'https://docs.python.org/': None,
}
