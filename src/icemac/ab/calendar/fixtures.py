from icemac.ab.calendar.category import Category
import icemac.ab.calendar.category
import icemac.ab.calendar.interfaces
import icemac.ab.calendar.testing
import icemac.addressbook.conftest
import icemac.addressbook.testing
import icemac.addressbook.utils
import pytest
import zope.component.hooks
import zope.publisher.browser


# Fixtures to create objects:


@pytest.fixture('function')
def RequestFactory():
    """Get a request object on the right skin layer."""
    def get_request(**kw):
        return zope.publisher.browser.TestRequest(
            skin=icemac.addressbook.browser.interfaces.IAddressBookLayer,
            **kw)
    return get_request


@pytest.fixture(scope='session')
def CategoryFactory():
    """Create an event category in the calendar."""
    def create_category(address_book, title, **kw):
        parent = address_book.calendar_categories
        with zope.component.hooks.site(address_book):
            name = icemac.addressbook.utils.create_and_add(
                parent, Category, title=title, **kw)
        return parent[name]
    return create_category


@pytest.fixture(scope='session')
def EventFactory():
    """Create an event in the calendar."""
    def create_event(address_book, **kw):
        return icemac.addressbook.testing.create(
            address_book, address_book.calendar,
            icemac.ab.calendar.interfaces.IEvent, **kw)
    return create_event


@pytest.fixture(scope='session')
def RecurringEventFactory():
    """Create a recurring event in its container."""
    def create_recurring_event(address_book, **kw):
        return icemac.addressbook.testing.create(
            address_book, address_book.calendar_recurring_events,
            icemac.ab.calendar.interfaces.IRecurringEvent, **kw)
    return create_recurring_event


# generally usable helper fixtures:


@pytest.fixture(scope='session')
def DateTime():
    """Fixture to ease handling of datetime objects."""
    return icemac.ab.calendar.testing.DateTimeClass()


@pytest.fixture('function')
def utc_time_zone_pref(TimeZonePrefFactory):
    """Set the time zone in the preferences to UTC."""
    return TimeZonePrefFactory('UTC')
