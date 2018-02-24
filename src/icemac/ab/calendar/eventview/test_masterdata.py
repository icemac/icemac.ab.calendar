from zope.security.interfaces import Unauthorized
from zope.testbrowser.browser import HTTPError
from zope.testbrowser.browser import LinkNotFoundError
import pytest

EVENT_VIEW_CONFIGURATION_ADD_TEXT = 'event view configuration'


def test_masterdata__Table__1(address_book, browser):
    """It allows to navigate to the event views list."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    browser.getLink('Event views').click()
    assert browser.url == browser.CALENDAR_MASTERDATA_EVENTVIEW_URL


def test_masterdata__Table__2(address_book, browser):
    """It renders a message if there are no event view configurations yet."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MASTERDATA_EVENTVIEW_URL)
    assert 'No event views defined yet.' in browser.contents


@pytest.mark.parametrize('login', ('cal-visitor', 'cal-editor'))
def test_masterdata__Table__3(address_book, browser, login):
    """It renders no add link for any calendar user."""
    browser.login(login)
    browser.open(browser.CALENDAR_MASTERDATA_EVENTVIEW_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink(EVENT_VIEW_CONFIGURATION_ADD_TEXT)


def test_masterdata__Table__4(address_book, browser):
    """It prevents access for anonymous."""
    browser.handleErrors = False  # needed to catch exception
    with pytest.raises(Unauthorized):
        browser.open(browser.CALENDAR_MASTERDATA_EVENTVIEW_URL)


def test_masterdata__Add__1(address_book, browser):
    """It allows administrators to add a new category in the list."""
    browser.login('mgr')
    browser.open(browser.CALENDAR_MASTERDATA_EVENTVIEW_URL)
    browser.getLink(EVENT_VIEW_CONFIGURATION_ADD_TEXT).click()
    assert browser.CALENDAR_EVENTVIEW_CONFIGURATION_ADD_URL == browser.url
    browser.getControl('title').value = 'default'
    browser.getControl('Add').click()
    assert '"default" added.' == browser.message
    # The new configuration shows up in the list:
    assert '>default<' in browser.contents


def test_masterdata__Add__2(
        address_book, EventViewConfigurationFactory, browser):
    """It prevents adding a new config with an already existing title."""
    EventViewConfigurationFactory(address_book, u'default')
    browser.login('mgr')
    browser.open(browser.CALENDAR_EVENTVIEW_CONFIGURATION_ADD_URL)
    browser.getControl('title').value = 'default'
    browser.getControl('Add').click()
    assert 'There were some errors.' in browser.contents
    assert 'This title is already used for an ' in browser.contents


@pytest.mark.parametrize('login', ('cal-visitor', 'cal-editor'))
def test_masterdata__Add__3(address_book, browser, login):
    """It is not accessible for any calendar user."""
    browser.login(login)
    with pytest.raises(HTTPError) as err:
        browser.open(browser.CALENDAR_EVENTVIEW_CONFIGURATION_ADD_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


def test_masterdata__Edit__1(
        address_book, EventViewConfigurationFactory, CategoryFactory, browser):
    """It allows to edit a category."""
    EventViewConfigurationFactory(address_book, u'default')
    CategoryFactory(address_book, u'foo')
    CategoryFactory(address_book, u'bar')
    browser.login('mgr')
    browser.open(browser.CALENDAR_MASTERDATA_EVENTVIEW_URL)
    browser.getLink('default').click()
    assert browser.CALENDAR_EVENTVIEW_CONFIGURATION_EDIT_URL == browser.url
    assert 'default' == browser.getControl('title').value
    browser.getControl('title').value = 'alternative'
    browser.getControl('start date').displayValue = ['3 days in past']
    browser.getControl('duration').displayValue = ['3 weeks']
    browser.getControl('categories').displayValue = ['bar']
    browser.getControl('show fields').displayValue = ['persons']
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    # The changed category name shows up in the list:
    assert 'alternative' in browser.contents
    browser.getLink('alternative').click()
    assert browser.getControl('title').value == 'alternative'
    assert browser.getControl('start date').displayValue == ['3 days in past']
    assert browser.getControl('duration').displayValue == ['3 weeks']
    assert browser.getControl('categories').displayValue == ['bar']
    assert browser.getControl('show fields').displayValue == ['persons']


def test_masterdata__Edit__2(
        address_book, EventViewConfigurationFactory, browser):
    """It prevents changing a category title to an existing one."""
    EventViewConfigurationFactory(address_book, u'default')
    EventViewConfigurationFactory(address_book, u'alternative')
    browser.login('mgr')
    browser.open(browser.CALENDAR_EVENTVIEW_CONFIGURATION_EDIT_URL)
    browser.getControl('title').value = 'alternative'
    browser.getControl('Apply').click()
    assert 'There were some errors.' in browser.contents
    assert 'This title is already used for an ' in browser.contents


@pytest.mark.parametrize('login', ('cal-visitor', 'cal-editor'))
def test_masterdata__Edit__3(
        address_book, EventViewConfigurationFactory, browser, login):
    """It allows calendar users only to see the event view configuration data.

    But they cannot change or delete them.
    """
    EventViewConfigurationFactory(address_book, u'foo')
    browser.login(login)
    browser.open(browser.CALENDAR_EVENTVIEW_CONFIGURATION_EDIT_URL)
    # There are no fields and no delete button:
    assert (['form.buttons.apply', 'form.buttons.cancel'] ==
            browser.all_control_names)


def test_masterdata__Delete__1(
        address_book, EventViewConfigurationFactory, browser):
    """It allows to delete an event view configuration."""
    EventViewConfigurationFactory(address_book, u'default')
    browser.login('mgr')
    browser.open(browser.CALENDAR_EVENTVIEW_CONFIGURATION_EDIT_URL)
    browser.getControl('Delete').click()
    assert browser.CALENDAR_EVENTVIEW_CONFIGURATION_DELETE_URL == browser.url
    assert ('Do you really want to delete this event view configuration?' in
            browser.contents)
    browser.getControl('Yes').click()
    assert '"default" deleted.' == browser.message


@pytest.mark.parametrize('login', ('cal-visitor', 'cal-editor'))
def test_masterdata__Delete__2(
        address_book, EventViewConfigurationFactory, browser, login):
    """It is not accessible for any calendar user."""
    EventViewConfigurationFactory(address_book, u'foo')
    browser.login(login)
    with pytest.raises(HTTPError) as err:
        browser.open(browser.CALENDAR_EVENTVIEW_CONFIGURATION_DELETE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)
