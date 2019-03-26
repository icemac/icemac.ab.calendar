This package provides a calendar feature for `icemac.addressbook`_.

.. _`icemac.addressbook` : https://pypi.org/project/icemac.addressbook/

Copyright (c) 2010-2019 Michael Howitz

This package is licensed under the MIT License, see LICENSE.txt inside the
package.

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

To run the tests yourself call::

  $ virtualenv-2.7 .
  $ bin/pip install zc.buildout
  $ bin/buildout -n
  $ bin/py.test
