from icemac.ab.calendar.interfaces import ICalendar, ICategories
from icemac.ab.calendar.interfaces import IRecurringEvents
from icemac.ab.calendar.eventview.interfaces import IEventViewContainer
from icemac.addressbook.addressbook import AddressBookCreated
from icemac.ab.calendar.install import install_calendar


def test_install__install_calendar__1(assert_address_book):
    """It creates an calendar attribute."""
    install_calendar(AddressBookCreated(assert_address_book.address_book))
    assert_address_book.has_attribute('calendar', ICalendar)
    assert_address_book.has_attribute('calendar_categories', ICategories)
    assert_address_book.has_attribute(
        'calendar_recurring_events', IRecurringEvents)
    assert_address_book.has_attribute(
        'calendar_eventviews', IEventViewContainer)


def test_install__install_calendar__2(assert_address_book):
    """It does not break if it gets called twice."""
    event = AddressBookCreated(assert_address_book.address_book)
    install_calendar(event)
    install_calendar(event)
    assert_address_book.has_attribute('calendar', ICalendar)
