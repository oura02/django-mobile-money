import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# Configuration Sphinx
project   = 'django-mobile-money'
copyright = '2026, OURA KONAN ROMEO'
author    = 'OURA KONAN ROMEO'
release   = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

templates_path   = ['_templates']
exclude_patterns = []
language         = 'fr'

html_theme        = 'sphinx_rtd_theme'
html_static_path  = ['_static']

html_theme_options = {
    'logo_only':           False,
    'navigation_depth':    4,
    'collapse_navigation': False,
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 'https://docs.djangoproject.com/en/stable/_objects/'),
}