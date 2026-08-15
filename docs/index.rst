package_name documentation
==========================

*SHORT TAGLINE FOR YOUR PACKAGE*

``package_name`` does [DESCRIBE WHAT YOUR PACKAGE DOES].


What's in ``package_name``?
============================

``package_name`` provides [DESCRIBE THE KEY COMPONENTS].

.. grid:: 2
    :class-container: component-grid

    .. grid-item:: :doc:`Module A <api/package_name>`

       Description of module A

    .. grid-item:: :doc:`Module B <api/package_name>`

       Description of module B


Getting started
===============

* Check out the :doc:`examples/getting_started` to get familiar with ``package_name``.
* Dive into the code itself in the API reference of :doc:`api/package_name`.


Installation
=============

Install the latest version by cloning the repository::

    git clone https://github.com/YOUR_ORG/package_name

We recommend using ``uv`` for managing the Python environment::

   uv venv --python=3.12
   source .venv/bin/activate

The package can then be installed directly::

    cd package_name
    uv pip install -e .             # Basic install
    uv pip install -e ".[dev]"      # For developers (tests, docs)

Or using ``uv sync``::

    uv sync
    uv sync --extra dev      # For developers


Contents
========

.. toctree::
   :maxdepth: 2
   :caption: API reference

   api/package_name

.. toctree::
   :maxdepth: 2
   :caption: Developer guide

   developer_guide/contributing

.. toctree::
   :maxdepth: 2
   :caption: Miscellaneous

   citing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
