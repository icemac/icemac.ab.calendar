import icemac.ab.calendar.category
import icemac.ab.calendar.interfaces
import icemac.ab.calendar.testing
import icemac.addressbook.conftest
import icemac.addressbook.testing
import icemac.addressbook.utils
import icemac.recurrence.conftest
import pytest


pytest_plugins = (
    'icemac.addressbook.fixtures',
    'icemac.ab.calendar.fixtures',
)


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
    assert icemac.addressbook.testing.CURRENT_CONNECTION is not None, \
        "The `browser` fixture needs a database fixture like `address_book`."
    return icemac.ab.calendar.testing.Browser(wsgi_app=browserWsgiAppS)


# generally usable helper fixtures:


@pytest.fixture(scope='function')
def sitemenu(browser):
    """Helper fixture to test the selections in the site menu.

    USABLE IN TESTS.

    """
    return icemac.addressbook.testing.SiteMenu


@pytest.fixture(scope='function')
def assert_address_book(address_book):
    """Fixture returning an object providing a custom address book asserts."""
    return icemac.addressbook.testing.AddressBookAssertions(address_book)


# Infrastructure fixtures


@pytest.yield_fixture(scope='session')
def zcmlS():
    """Load calendar ZCML on session scope."""
    layer = icemac.addressbook.testing.SecondaryZCMLLayer(
        'Calendar', __name__, icemac.ab.calendar)
    layer.setUp()
    yield layer
    layer.tearDown()


@pytest.yield_fixture(scope='session')
def zodbS(zcmlS):
    """Create an empty test ZODB."""
    for zodb in icemac.addressbook.testing.pyTestEmptyZodbFixture():
        yield zodb


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
