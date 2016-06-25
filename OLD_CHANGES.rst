==========================
 Changelog older versions
==========================

Changelog of releases more than 3 versions behind current version.

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

- Allow calendar users to edit their username and/or password in master
  data.


1.2.0 (2014-01-02)
==================

- Selected month is kept in session, to ease editing in another month than
  the current one. (requiring at least `icemac.addressbook 2.2`)

- Bugfix: empty field values are no longer displayed in the calendar.


1.1.0 (2013-12-31)
==================

- Add option to select calendar as start page. (thus requring at least
  `icemac.addressbook 2.1`).


1.0.1 (2013-12-26)
==================

- Bugfix: Successfully render calendar if month name contains an umlaut.


1.0.0 (2013-11-03)
==================

- Initial release.
