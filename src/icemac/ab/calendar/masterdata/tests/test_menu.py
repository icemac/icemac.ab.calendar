from __future__ import unicode_literals
from zope.security.interfaces import Unauthorized
import pytest


@pytest.fixture(scope='function')
def master_data_menu(address_book, browser, sitemenu):
    """Fixture to test the calendar master data menu."""
    browser.login('mgr')
    return sitemenu(browser, 4, 'Master data', browser.CALENDAR_MASTERDATA_URL)


def test_menu__master_data_menu__1(master_data_menu):
    """Asserting that the menu with the index 4 is calendar master data."""
    master_data_menu.assert_correct_menu_item_is_tested()


def test_menu__master_data_menu__2(master_data_menu):
    """The master data tab is selected on calendar master data overview."""
    assert master_data_menu.item_selected(master_data_menu.menu_item_URL)


def test_menu__master_data_menu__3(master_data_menu):
    """The master data tab is selected on event categories."""
    assert master_data_menu.item_selected(
        master_data_menu.browser.CALENDAR_CATEGORIES_LIST_URL)


def test_menu__master_data_menu__4(master_data_menu):
    """The master data tab is selected on edit display."""
    master_data_menu.item_selected(
        master_data_menu.browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL)


def test_menu__CalendarMasterDataManager__1(address_book, browser):
    """It allows to navigate to the calendar master data."""
    browser.login('cal-visitor')
    browser.open(browser.MASTER_DATA_URL)
    browser.getLink('Calendar', index=1).click()
    assert browser.CALENDAR_MASTERDATA_URL == browser.url
    assert 'Event categories' in browser.contents


def test_menu__CalendarMasterDataManager__2(address_book, browser):
    """It prevents access for anonymous."""
    browser.handleErrors = False  # needed to catch exception
    with pytest.raises(Unauthorized):
        browser.open(browser.CALENDAR_MASTERDATA_URL)
