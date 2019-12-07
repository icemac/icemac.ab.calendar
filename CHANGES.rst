===========
 Changelog
===========

3.4 (unreleased)
================

- On mobile devices:

    + fix rendering of the calendar by replacing the tabular rendering by a
      vertical one like the print version.

    + replace secondary horizontal menu with a vertical one hidden behind a
      burger icon.

3.3 (2019-10-01)
================

- Consider customization of pre-defined fields in forms.

- Update the ZCML configuration and CSS to changes in
  `icemac.addressbook >= 9`.


3.2 (2018-10-13)
================

- Drop dependency on `decorator` package.

- Update to changes in test infrastructure in `icemac.addressbook >= 8.0`.

- Change installation procedure from `bootstrap.py` to `virtualenv`,
  see `README.txt`.


3.1 (2018-08-03)
================

- Improve readability and usability of list views.

- List views now also return the events of the last displayed day.

- Adapt configuration, CSS and tests to `icemac.addressbook >= 7.0`.

- Fix the close URL of the list views so it does not stick to the list views.

- No longer render the submit button in the calendar list view as the drop
  downs have auto-submit.

- Change license from ZPL to MIT.


Older versions
==============

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.ab.calendar/raw/default/OLD_CHANGES.rst
