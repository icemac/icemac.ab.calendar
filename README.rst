.. image:: https://travis-ci.com/icemac/icemac.ab.calendar.svg?branch=master
   :target: https://travis-ci.com/icemac/icemac.ab.calendar

.. image:: https://coveralls.io/repos/github/icemac/icemac.ab.calendar/badge.svg
   :target: https://coveralls.io/github/icemac/icemac.ab.calendar

.. image:: https://img.shields.io/pypi/v/icemac.ab.calendar.svg
   :target: https://pypi.python.org/pypi/icemac.ab.calendar/
   :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/icemac.ab.calendar.svg
   :target: https://pypi.org/project/icemac.ab.calendar/
   :alt: Supported Python versions

This package provides a calendar feature for `icemac.addressbook`_.

.. _`icemac.addressbook` : https://pypi.org/project/icemac.addressbook/

Copyright (c) 2010-2020 Michael Howitz

This package is licensed under the MIT License, see LICENSE.txt inside the
package.

.. contents::

=========
 Hacking
=========

Source code
===========

Get the source code::

   $ git clone https://github.com/icemac/icemac.ab.calendar

or fork me at: https://github.com/icemac/icemac.ab.calendar

Running the tests
=================

To run the tests yourself call::

  $ virtualenv-2.7 .
  $ bin/pip install zc.buildout
  $ bin/buildout -n
  $ bin/py.test
