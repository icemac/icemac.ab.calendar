from icemac.ab.calendar.category import Category
from mock import patch
import datetime
import icemac.ab.calendar.category
import icemac.ab.calendar.interfaces
import icemac.ab.calendar.testing
import icemac.addressbook.conftest
import icemac.addressbook.testing
import icemac.addressbook.utils
import icemac.recurrence.conftest
import pytest
import pytz
import zope.component.hooks
import zope.publisher.browser


pytest_plugins = 'icemac.addressbook.conftest'


# Fixtures to set-up infrastructure which are usable in tests:


@pytest.yield_fixture(scope='function')
def address_book(addressBookConnectionF):
    """Get the address book with calendar as site."""
    for address_book in icemac.addressbook.conftest.site(
            addressBookConnectionF):
        yield address_book


@pytest.fixture(scope='function')
def browser(browserWsgiAppS):
    """Fixture for testing with zope.testbrowser."""
    assert icemac.addressbook.conftest.CURRENT_CONNECTION is not None, \
        "The `browser` fixture needs a database fixture like `address_book`."
    return icemac.ab.calendar.testing.Browser(wsgi_app=browserWsgiAppS)


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
    return DateTimeClass()


@pytest.yield_fixture('function')
def TimeZonePrefFactory():
    """Factory to set the time zone in the preferences."""
    patchers = []

    def set_time_zone_pref(time_zone_name):
        patcher = patch(
            'icemac.addressbook.preferences.utils.get_time_zone_name',
            return_value=time_zone_name)
        patcher.start()
        patchers.append(patcher)
    yield set_time_zone_pref
    while patchers:
        patchers.pop().stop()


@pytest.fixture('function')
def utc_time_zone_pref(TimeZonePrefFactory):
    """Set the time zone in the preferences to UTC."""
    return TimeZonePrefFactory('UTC')


# Infrastructure fixtures


@pytest.yield_fixture(scope='session')
def zcmlS(zcmlS):
    """Load calendar ZCML on session scope."""
    layer = icemac.addressbook.testing.SecondaryZCMLLayer(
        'Calendar', __name__, icemac.ab.calendar, [zcmlS])
    layer.setUp()
    yield layer
    layer.tearDown()


@pytest.yield_fixture(scope='session')
def addressBookS(zcmlS, zodbS):
    """Create an address book for the session."""
    for zodb in icemac.addressbook.conftest.pyTestAddressBookFixture(
            zodbS, 'CalendarS'):
        yield zodb


@pytest.yield_fixture(scope='function')
def addressBookConnectionF(addressBookS):
    """Get the connection to the right demo storage."""
    for connection in icemac.addressbook.conftest.pyTestStackDemoStorage(
            addressBookS, 'CalendarF'):
        yield connection


# Fixture helpers

class DateTimeClass(icemac.recurrence.conftest.DateTimeClass):
    """Helper class to create and format datetime objects."""

    @property
    def now(self):
        return pytz.utc.localize(datetime.datetime.now())

    def format(self, dt, force_date=False):
        """Format a datetime to the format needed in testbrowser."""
        if isinstance(dt, datetime.datetime) and not force_date:
            return dt.strftime('%y/%m/%d %H:%M')
        else:
            return self.format_date(dt)

    def format_date(self, dt):
        return "{0.year} {0.month} {0.day} ".format(dt)

    @property
    def today_8_32_am(self):
        """Get a datetime object for today with fixed time."""
        return datetime.datetime.combine(
            datetime.date.today(), datetime.time(8, 32, tzinfo=pytz.utc))

    @staticmethod
    def add(dt, days):
        """Add some days to `dt`."""
        return dt + datetime.timedelta(days=days)
