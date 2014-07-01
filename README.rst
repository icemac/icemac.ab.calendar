This package provides a calendar feature for `icemac.addressbook`_.

.. _`icemac.addressbook` : http://pypi.python.org/pypi/icemac.addressbook

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
  $ bin/buildout
  $ bin/test
