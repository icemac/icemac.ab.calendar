# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
from .interfaces import DATE_INDEX
import icemac.ab.calendar.calendar
import icemac.ab.calendar.category
import icemac.ab.calendar.interfaces
import icemac.addressbook.addressbook
import icemac.addressbook.utils
import zc.catalog.catalogindex
import zope.catalog.interfaces
import zope.component


@zope.component.adapter(
    icemac.addressbook.addressbook.AddressBookCreated)
def install_calendar(event):
    "Install the calendar in the newly created addressbook."
    with icemac.addressbook.utils.site(event.address_book) as address_book:
        icemac.addressbook.addressbook.create_and_register(
            address_book, 'calendar', icemac.ab.calendar.calendar.Calendar,
            icemac.ab.calendar.interfaces.ICalendar)
        icemac.addressbook.addressbook.create_and_register(
            address_book, 'calendar_categories',
            icemac.ab.calendar.category.CategoryContainer,
            icemac.ab.calendar.interfaces.ICategories)
        update_calendar_infrastructure(address_book)


def update_calendar_infrastructure(address_book):
    """Update the calendar infrastructure to install new components."""
    with icemac.addressbook.utils.site(address_book):
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        if DATE_INDEX not in catalog:
            catalog[DATE_INDEX] = zc.catalog.catalogindex.DateTimeValueIndex(
                'datetime', icemac.ab.calendar.interfaces.IEvent,
                resolution=1)
            catalog.updateIndex(catalog.get(DATE_INDEX))
        icemac.addressbook.addressbook.add_entity_to_order(
            address_book.orders, icemac.ab.calendar.interfaces.IEvent)
