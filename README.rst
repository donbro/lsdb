lsdb -- a multi-tool for your metadata
======================================

|Build Status|

Introduction
============

The **lsdb** utility and its associated modules convert between filesystem metadata, various serialized 
data format files (json, xml, etc.) and database schema.
 
``lsdb`` is a tool to make managing your lsdb symlinks in ``$HOME``
easy, allowing you to keep all your lsdb in a single directory.

Command-Line Interface
---------

``-a, --add <file...>``
    Add lsdb(s) to the repository.

Install
--------

To use (with caution), simply do::

    >>> import lsdb
    >>> print lsdb.joke()

* `Installation <https://pip.pypa.io/en/stable/installing.html>`_
* `Documentation <https://pip.pypa.io/>`_
* `Changelog <https://pip.pypa.io/en/stable/news.html>`_
* `Github Page <https://github.com/pypa/pip>`_

Here is a program to parse ``"Hello, World!"`` (or any greeting of the form
``"salutation, addressee!"``):

.. code:: python

    from lsdb import files, database
    greet = Word(alphas) + "," + Word(alphas) + "!"
    hello = "Hello, World!"
    print(hello, "->", greet.parseString(hello))

The program outputs the following::

    Hello, World! -> ['Hello', ',', 'World', '!']

The Python representation of the grammar is quite readable, owing to the
self-explanatory class names, and the use of '+', '|' and '^' operator
definitions.


.. image:: https://img.shields.io/lsdb/v/pip.svg
   :target: https://pypi.python.org/lsdb/lsdb

.. image:: https://img.shields.io/travis/pypa/pip/master.svg
   :target: http://travis-ci.org/pypa/lsdb

.. image:: https://img.shields.io/appveyor/ci/pypa/lsdb.svg
   :target: https://ci.appveyor.com/project/pypa/lsdb/history

.. image:: https://readthedocs.org/projects/lsdb/badge/?version=stable
   :target: https://pip.pypa.io/en/stable
