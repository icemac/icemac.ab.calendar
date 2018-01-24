from zope.testbrowser.browser import LinkNotFoundError, HTTPError
from zope.security.interfaces import Unauthorized
import pytest


EVENT_CATEGORY_ADD_TEXT = 'event category'


def test_category__Table__1(address_book, browser):
    """It allows to navigate to the category list view."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    browser.getLink('Event categories').click()
    assert browser.CALENDAR_CATEGORIES_LIST_URL == browser.url


def test_category__Table__2(address_book, browser):
    """It renders a message if there are no categories yet."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_CATEGORIES_LIST_URL)
    assert 'No event categories defined yet.' in browser.contents


def test_category__Table__3(address_book, browser):
    """It renders no add link for a calendar visitor."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_CATEGORIES_LIST_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink(EVENT_CATEGORY_ADD_TEXT)


def test_category__Table__4(address_book, browser):
    """It prevents access for anonymous."""
    browser.handleErrors = False  # needed to catch exception
    with pytest.raises(Unauthorized):
        browser.open(browser.CALENDAR_CATEGORIES_LIST_URL)


def test_category__Add__1(address_book, browser):
    """It allows to add a new category in the list."""
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_CATEGORIES_LIST_URL)
    browser.getLink(EVENT_CATEGORY_ADD_TEXT).click()
    assert browser.CALENDAR_CATEGORY_ADD_URL == browser.url
    browser.getControl('event category').value = 'birthday'
    browser.getControl('Add').click()
    assert '"birthday" added.' == browser.message
    # The new category shows up in the list:
    assert '>birthday<' in browser.contents


def test_category__Add__2(address_book, CategoryFactory, browser):
    """It prevents adding a new category with an already existing title."""
    CategoryFactory(address_book, u'birthday')
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_CATEGORY_ADD_URL)
    browser.getControl('event category').value = 'birthday'
    browser.getControl('Add').click()
    assert 'There were some errors.' in browser.contents
    assert 'This category already exists.' in browser.contents


def test_category__Add__3(address_book, browser):
    """It is not accessible for a calendar visitor."""
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.CALENDAR_CATEGORY_ADD_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


def test_category__Edit__1(address_book, CategoryFactory, browser):
    """It allows to edit a category."""
    CategoryFactory(address_book, u'birthday')
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_CATEGORIES_LIST_URL)
    browser.getLink('birthday').click()
    assert browser.CALENDAR_CATEGORY_EDIT_URL == browser.url
    assert 'birthday' == browser.getControl('event category').value
    browser.getControl('event category').value = 'wedding day'
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    # The changed category name shows up in the list:
    assert 'wedding day' in browser.contents


def test_category__Edit__2(address_book, CategoryFactory, browser):
    """It prevents changing a category title to an existing one."""
    CategoryFactory(address_book, u'birthday')
    CategoryFactory(address_book, u'wedding day')
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_CATEGORY_EDIT_URL)
    browser.getControl('event category').value = 'wedding day'
    browser.getControl('Apply').click()
    assert 'There were some errors.' in browser.contents
    assert 'This category already exists.' in browser.contents


def test_category__Edit__3(address_book, CategoryFactory, browser):
    """It allows a calendar visitor only to see the category data.

    But he cannot change or delete them.
    """
    CategoryFactory(address_book, u'foo')
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_CATEGORY_EDIT_URL)
    # There are no fields and no delete button:
    assert (['form.buttons.apply', 'form.buttons.cancel'] ==
            browser.all_control_names)


def test_category__Delete__1(address_book, CategoryFactory, browser):
    """It allows to delete a category."""
    CategoryFactory(address_book, u'birthday')
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_CATEGORY_EDIT_URL)
    browser.getControl('Delete').click()
    assert browser.CALENDAR_CATEGORY_DELETE_URL == browser.url
    assert ('Do you really want to delete this event category?' in
            browser.contents)
    browser.getControl('Yes').click()
    assert '"birthday" deleted.' == browser.message


def test_category__Delete__2(
        address_book, CategoryFactory, EventFactory, browser):
    """It assures that a used category cannot be deleted."""
    EventFactory(
        address_book, category=CategoryFactory(address_book, u'birthday'))
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_CATEGORY_DELETE_URL)
    with pytest.raises(LookupError):
        browser.getControl('Delete')


def test_category__Delete__3(address_book, CategoryFactory, browser):
    """It is not accessible for a calendar visitor."""
    CategoryFactory(address_book, u'foo')
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.CALENDAR_CATEGORY_DELETE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)
