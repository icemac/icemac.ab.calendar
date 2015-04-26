This package provides a calendar feature for `icemac.addressbook`_.

.. _`icemac.addressbook` : http://pypi.python.org/pypi/icemac.addressbook

Copyright (c) 2008-2015 Michael Howitz

All Rights Reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.

.. contents::

=========
 Hacking
=========

Source code
===========

Get the source code::

   $ hg clone https://bitbucket.org/icemac/icemac.ab.calendar

or fork me on: https://bitbucket.org/icemac/icemac.ab.calendar

Running the tests
=================

.. Currently the tests on Travis-CI are not run:
.. .. image:: https://secure.travis-ci.org/icemac/icemac.ab.calendar.png
..    :target: https://travis-ci.org/icemac/icemac.ab.calendar

To run the tests yourself call::

  $ python2.7 bootstrap.py
  $ bin/buildout -n
  $ bin/py.test
