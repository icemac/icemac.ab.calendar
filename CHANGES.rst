===========
 Changelog
===========

1.6.0 (unreleased)
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


1.4.0 (2014-03-07)
==================

- Color the current day on the calendar.


1.3.1 (2014-02-09)
==================

- Fix the widh of the calendar to the width of the window.


1.3.0 (2014-02-08)
==================

- Made selection of month for display two drop downs for month and year.

- Added calendar view displaying a whole year.

- Allow calendar users to edit their username and/or password in master data.


Older versions
==============

See OLD_CHANGES.rst inside the package.
