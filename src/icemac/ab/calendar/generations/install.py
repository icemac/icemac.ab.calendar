# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
"""Initial generation."""


import icemac.ab.calendar.install
import icemac.addressbook.addressbook
import icemac.addressbook.generations.utils


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(address_book):
    """Installs the calendar into each existing address book."""
    icemac.ab.calendar.install.install_calendar(
        icemac.addressbook.addressbook.AddressBookCreated(address_book))
