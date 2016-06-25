===========
 Changelog
===========

1.9 (2016-06-25)
================

- Allow to restrict which persons are listed in the person list on the event
  using: Master Data > Calendar > Settings > Person keyword.


1.8 (2016-04-16)
================

Bugfixes
--------

- Fix a bug with daylight saving time adding one hour to each event during DST.

- Normalize non-recurring events to UTC to fix possibly wrong local time zone
  values. **Caution:** Some events could not be fixed because they already have
  a wrong time with the UTC time zone. But only some of the events with a UTC
  time zone seem to have this offset. These ones have to be fixed by hand.
  Sorry for the inconvenience.

- Listing of recurring events in calendar master data no longer displays a time
  for whole-day events.

Features
--------

- Add a special style sheet for printing to render the calendar as a list on
  paper. (Works in Safari, Firefox, Google Chrome and
  Internet Explorer >= 10.x)


1.7.1 (2016-03-12)
==================

- Bugfix: Since 1.7.0 locally defined calendar users no longer where able to
  edit events.

1.7.0 (2016-03-05)
==================

Features
--------

- Add new `daily` recurrence for recurring events.

- Add end date to recurring events.

- Newlines in the `nodes` field now lead to new items in the calendar view for
  each line.

- Allow events to take place the whole day.

Bugfixes
--------

- Selecting a user defined field for display in calendar view resulted in an
  error when displaying recurred events.

Other
-----

- No longer use `unittest2` as it was included in Python 2.7.

- Lint JS code.

- Use py.test as new test runner.

- Use package `icemac.recurrence` which was extracted for reuse from here.

Older versions
==============

See OLD_CHANGES.rst inside the package.
