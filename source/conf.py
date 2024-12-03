# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ecommerce_saade_souaiby'
copyright = '2024, Saade Souaiby'
author = 'Saade Souaiby'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',           # Automatically document Python docstrings
    'sphinx.ext.autodoc.typehints', # Include type hints in the docs
    'sphinx.ext.napoleon'           # Parse NumPy and Google style docstrings
]

templates_path = ['_templates']
exclude_patterns = []
autodoc_mock_imports = ['database']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

import os
import sys
sys.path.insert(0, os.path.abspath('C:/Users/jgsou/OneDrive/Desktop/AUB/EECE 435L/Final Project/ecommerce_Saade_Souaiby/services'))

