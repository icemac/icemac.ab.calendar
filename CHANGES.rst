===========
 Changelog
===========

3.2 (unreleased)
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


3.0 (2018-03-16)
================

Backward incompatible changes
-----------------------------

- ``.calendar.Calendar.get_events()`` now expects two arguments: start and end.
  The previous functionality of ``get_events()`` is now provided by
  ``get_events_for_month()``

- Move ``.browser.renderer.interfaces.IEventDescription`` and
  ``.browser.renderer.interfaces.UnknownLanguageError`` to
  ``.browser.interfaces``.

Features
--------

- Add configurable list views instead of the fix month list view.
  (See Master data > Calendar > List views for the configuration.)


Other changes
-------------

- Adapt code to `icemac.addressbook >= 6.0`.


Older versions
==============

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.ab.calendar/raw/default/OLD_CHANGES.rst
