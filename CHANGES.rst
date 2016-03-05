===========
 Changelog
===========

1.7.0 (2016-03-05)
==================

Features
--------

- Add new `daily` recurrence for recurring events.

- Add end date to recurring events.

- Newlines in the `nodes` field now lead to new items in the caöendar view for
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

1.6.0 (2014-12-16)
==================

- Add new recurrences for recurring events:

  * biweekly,
  * nth weekday of month,
  * nth weekday every other month
  * nth weekday from end of month
  * nth weekday from end of other month
  * yearly

- Display actual recurrences in recurrence event listing in master data.

- If there are two reccurred events matching in date, time and category only
  the one is rendered thats recurring event occurres more seldomly.

- Day numbers are now add-links to create a new event for the day.


1.5.0 (2014-07-01)
==================

Features
--------

- Add concept of recurring events, see master data of calendar to configure them.

Bug fixes
---------

- The calendar tab in the main menu is now highlighted when the calendar, an
  event or calendar masterdata is displayed.

- Events are displayed on the correct local day (according to chosen time
  zone) even if it is another one than the one in UTC.

Other
-----

- Adapt tests and code to changes in `icemac.addressbook 2.5`.

- Add py.test to run the tests.

Older versions
==============

See OLD_CHANGES.rst inside the package.
