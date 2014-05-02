===========
 Changelog
===========

1.5.0 (unreleased)
==================

Features
--------

- Add concept of recurring events, in user interface see master data of
  calendar.

Bug fixes
---------

- The calendar tab in the main menu is now highlighted when the calendar, an
  event or calendar masterdata is displayed.

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


1.2.0 (2014-01-02)
==================

- Selected month is kept in session, to ease editing in another month than
  the current one. (requiring at least `icemac.addressbook 2.2`)

- Bugfix: empty field values are no longer displayed in the calendar.

Older versions
==============

See OLD_CHANGES.rst inside the package.
