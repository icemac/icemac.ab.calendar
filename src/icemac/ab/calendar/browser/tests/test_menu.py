from __future__ import unicode_literals
import pytest


@pytest.fixture(scope='function')
def calendar_menu(address_book, browser, sitemenu):
    """Fixture to test the calendar menu."""
    browser.login('cal-editor')
    return sitemenu(browser, 0, 'Calendar', browser.CALENDAR_OVERVIEW_URL)


def test_menu__calendar_menu__1(calendar_menu):
    """Asserting that the menu with the index 0 is `Calendar`."""
    calendar_menu.assert_correct_menu_item_is_tested()


def test_menu__calendar_menu__2(calendar_menu):
    """The calendar tab is selected on the calendar overview."""
    assert calendar_menu.item_selected(calendar_menu.menu_item_URL)


def test_menu__calendar_menu__3(calendar_menu):
    """The calendar tab is not selected on master data."""
    assert not calendar_menu.item_selected(
        calendar_menu.browser.MASTER_DATA_URL)


def test_menu__calendar_menu__4(calendar_menu):
    """The calendar tab is selected on the calendar year view."""
    assert calendar_menu.item_selected(
        calendar_menu.browser.CALENDAR_YEAR_OVERVIEW_URL)


def test_menu__calendar_menu__5(address_book, calendar_menu, EventFactory):
    """The calendar tab is selected on the event clone view."""
    EventFactory(address_book)
    calendar_menu.item_selected(calendar_menu.browser.EVENT_CLONE_URL)


def test_menu__CalendarMenuItem__1(address_book, browser):
    """It allows to navigate the to calendar.

    The calendar view defaults to the month overview.
    """
    browser.login('cal-editor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert browser.CALENDAR_OVERVIEW_URL == browser.getLink('Calendar').url
    browser.getLink('Calendar').click()
    assert browser.CALENDAR_MONTH_OVERVIEW_URL == browser.url
