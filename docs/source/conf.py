# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import yaml
from unittest import mock

from hydra.experimental import compose, initialize
from omegaconf import OmegaConf


rel_root_path = "./../../"
abs_root_path = os.path.abspath(rel_root_path)
sys.path.insert(0, abs_root_path)


# -- Project information -----------------------------------------------------
with open(os.path.join(abs_root_path, "package_metadata.yaml"), "r") as f:
    pm = yaml.safe_load(f)

release = pm["__version__"]
project = pm["__name__"]
author = pm["__author__"]
copyright = pm["__copyright__"]

# -- YAML main to print the config into  ---------------------------------------------------
# We need to concatenate configs into a single file using hydra
with initialize(config_path=os.path.join(rel_root_path, "configs/"), job_name="config"):
    cfg = compose(config_name="config")
    print(OmegaConf.to_yaml(cfg))
    OmegaConf.save(cfg, "./apidoc/default_config.yml", resolve=False)

# -- General configuration ---------------------------------------------------

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = "en"

# generate autosummary pages
autosummary_generate = True

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
needs_sphinx = "4.0"
extensions = [
    "sphinx.ext.napoleon",  # Supports google-style docstrings
    "sphinx.ext.autodoc",  # auto-generates doc fgrom docstrings
    "sphinx.ext.intersphinx",  # link to other docs
    "sphinx.ext.viewcode",  # creates links to view code sources in a new web page
    "sphinx.ext.githubpages",  # creates .nojekyll file to publish the doc on GitHub Pages.
    "myst_parser",  # supports markdown syntax for doc pages
    "sphinx_paramlinks",  # allow to reference params, which is done in pytorch_lightning
    "sphinxnotes.mock",  # ignore third-parties directive suche as "testcode" - see "mock_directive" args below
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "collapse_navigation": False,
    "display_version": True,
    "navigation_depth": 2,
}


intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    # TODO "unknown or unsupported inventory version" error for numpy doc.
    # 'numpy': ('http://docs.scipy.org/doc/numpy', None),
    "pandas": ("http://pandas.pydata.org/pandas-docs/dev", None),
    "torch": ("https://pytorch.org/docs/master", None),
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
modindex_common_prefix = ["lidar_multiclass."]

to_mock = [
    # "torch",
    "comet_ml",
    "tqdm",
    "pdal",
    "python-pdal",
    "hydra",
    "laspy",
    "torch_geometric",
    "dotenv",
    "torch_points_kernels",
    "torchmetrics",
    "torchmetrics.functional",
    "torchmetrics.functional.classification",
    "torchmetrics.functional.classification.jaccard",
]


try:
    import torch  # noqa
except ImportError:
    for m in to_mock:
        sys.modules[m] = mock.Mock(name=m)
    sys.modules["torch"].__version__ = "1.10"  # fake version
    HAS_TORCH = False
else:
    HAS_TORCH = True

autodoc_mock_imports = []
for m in ["numpy", "pdal", "pdal", "dotenv", "laspy", "torch_points_kernels"]:
    autodoc_mock_imports.append(m)

mock_directives = ["testcode"]
