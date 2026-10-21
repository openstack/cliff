# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'openstackdocstheme',
    'reno.sphinxext',
]

# openstackdocstheme options
openstackdocs_repo_name = 'openstack/cliff'
openstackdocs_auto_name = False
openstackdocs_bug_project = 'cliff'
openstackdocs_bug_tag = 'doc'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'cliff Release Notes'
copyright = '2012-present, cliff Developers'

# Release notes do not need a version number in the title, they
# cover multiple releases.
# The full version, including alpha/beta/rc tags.
release = ''
# The short X.Y version.
version = ''

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'native'


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'openstackdocs'


# -- Options for LaTeX output ---------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        'index',
        'cliffReleaseNotes.tex',
        'cliff Release Notes Documentation',
        'cliff Developers',
        'manual',
    ),
]


# -- Options for Internationalization output ------------------------------
locale_dirs = ['locale/']
