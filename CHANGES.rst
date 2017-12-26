===========
 Changelog
===========

2.3 (2017-12-26)
================

- Add breadcrumbs.

- Fix rendering of month list:

  + day numbers in calendar for read-only users are now the same size as for
    r/w users.

  + the dots in front of text when rendering multiple items per event no longer
    overlap with previous text.

  + when printing it is rendered like the month calendar.

- Fix printing view of month list to render the event title first and align
  day numbers right.

- Fix printing view of year calendar to render each month on a single page.

- Change `zope.interface.implements[Only]` and `zope.component.adapts` to
  class decorators.

- Adapt the code to `icemac.addressbook >= 5.0`.

- Also release as wheel.

2.2 (2017-05-16)
================

Features
--------

- Add a month list view which looks like the print version of the month view.

Bug fixes
---------

- Allow to delete a recurred event and put a new event with the same category
  into its place. Before this fix the new event might not be displayed.


2.1.1 (2017-04-09)
==================

- Fix icons of links introduced in version 2.1 to be rendered equally on
  Firefox, Safari, Internet Explorer and Chrome.


2.1 (2017-04-08)
================

Features
--------

- Add links in month view to easily access the previous resp. next month.

- Rename the links to the month view and to the year view and add titles to
  them.


Other changes
-------------

- Bring the test coverage to 100 % including the tests itself and the test
  infrastructure but without the need to run the selenium tests to achieve
  this.

- Update to changes in test infrastructure in `icemac.addressbook >= 4.0`.


Older versions
==============

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.ab.calendar/raw/tip/OLD_CHANGES.rst
