# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt

import icemac.ab.calendar.calendar
import icemac.ab.calendar.category
import icemac.ab.calendar.interfaces
import icemac.addressbook.addressbook
import zope.component


@zope.component.adapter(
    icemac.addressbook.addressbook.AddressBookCreated)
def install_calendar(event):
    "Install the calendar in the newly created addressbook."
    address_book = event.address_book
    icemac.addressbook.addressbook.create_and_register(
        address_book, 'calendar', icemac.ab.calendar.calendar.Calendar,
        icemac.ab.calendar.interfaces.ICalendar)
    icemac.addressbook.addressbook.create_and_register(
        address_book, 'calendar_categories',
        icemac.ab.calendar.category.CategoryContainer,
        icemac.ab.calendar.interfaces.ICategories)
