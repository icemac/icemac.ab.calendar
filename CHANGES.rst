===========
 Changelog
===========

2.1.2 (2017-05-14)
==================

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


2.0 (2017-02-04)
================

Backward incompatible changes
-----------------------------

- Update test infrastructure to `icemac.addressbook >= 3.0`, thus update to
  `py.test >= 2.8`. The fixtures which can be reused where moved to
  ``icemac.ab.calendar.fixtures``. ``icemac.ab.calendar.conftest`` should no
  longer be used from foreign packages as this leads to problems with the new
  py.test version.


Bugs
----

- The computation of Biweekly events was fixed: There are now always two weeks
  between the events. Previously it could only be one if the recurrence in the
  previous month was in the last week of the month.

- Fix the bug with daylight saving time adding one hour to each event during
  DST for the year calendar which was already fixed for the month calendar in
  version 1.8.


1.12 (2017-01-21)
=================

- Adapt code so `grokcore.component >= 2.6` can be used.

- Fix sort order of events with the same datetime again. They are now
  sorted by the title of the category.

- Adapt styling to `icemac.addressbook >= 2.10`.


Older versions
==============

See OLD_CHANGES.rst inside the package.
