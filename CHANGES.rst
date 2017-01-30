===========
 Changelog
===========

2.0 (unreleased)
================

Backward incompatible changes
-----------------------------

- Update test infrastructure to `icemac.addressbook >= 3.0`, thus update to
  `py.test >= 2.8`. The fixtures which can be reused where moved to
  ``icemac.ab.calendar.fixtures``. ``icemac.ab.calendar.conftest`` should no
  longer be used from foreign packages as this leads to problems with the new
  py.test version.


Bug fixtures
------------

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


1.11.2 (2017-01-09)
===================

- Stabilize the sort order of events with the same datetime. They are now
  sorted by category.


1.11.1 (2017-01-07)
===================

- Fix an error in calendar display when rendering a user defined field which is
  only defined on IEvent but not on IRecurringEvent.


1.11 (2017-01-06)
=================

- Bring branch test coverage to 100 %.

- Adapt code and role configuration to `icemac.addressbook >= 2.9`.


1.10 (2016-08-28)
=================

- Add some infrastructure for `icemac.ab.calexport`.


Older versions
==============

See OLD_CHANGES.rst inside the package.
