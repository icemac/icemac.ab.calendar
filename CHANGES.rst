===========
 Changelog
===========

1.11.3 (2017-01-12)
===================

- Adapt code so `grokcore.component >= 2.6` can be used.

- Fix sort order of events with the same datetime again. They are now
  sorted by the title of the category.


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


1.9 (2016-06-25)
================

- Allow to restrict which persons are listed in the person list on the event
  using: Master Data > Calendar > Settings > Person keyword.


Older versions
==============

See OLD_CHANGES.rst inside the package.
