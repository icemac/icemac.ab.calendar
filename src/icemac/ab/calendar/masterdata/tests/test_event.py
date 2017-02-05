from __future__ import unicode_literals

from ..event import StartColumn
from icemac.ab.calendar.event import BaseEvent
from zope.testbrowser.browser import LinkNotFoundError, HTTPError
from zope.security.interfaces import Unauthorized
import pytest
import pytz


RECURRING_EVENT_ADD_TEXT = 'recurring event'


def test_event__Table__1(address_book, browser):
    """It allows to navigate to the recurring events list view."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    browser.getLink('Recurring Events').click()
    assert browser.CALENDAR_RECURRING_EVENTS_LIST_URL == browser.url


def test_event__Table__2(address_book, browser):
    """It renders a message if there are no recurring events yet."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_RECURRING_EVENTS_LIST_URL)
    assert 'No recurring events defined yet.' in browser.contents


def test_event__Table__3(address_book, browser):
    """It renders no add link for a calendar visitor."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_RECURRING_EVENTS_LIST_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink(RECURRING_EVENT_ADD_TEXT)


def test_event__Table__4(address_book, browser):
    """It prevents access for anonymous."""
    browser.handleErrors = False  # needed to catch exception
    with pytest.raises(Unauthorized):
        browser.open(browser.CALENDAR_RECURRING_EVENTS_LIST_URL)


def test_event__StartColumn__renderCell__1(
        DateTime, RequestFactory, utc_time_zone_pref):
    """It renders date and time on a non-whole-day event."""
    event = BaseEvent()
    event.datetime = DateTime(
        2016, 3, 10, 8, 32, tzinfo=pytz.timezone('Europe/Berlin'))
    event.whole_day_event = False
    col = StartColumn(None, RequestFactory(), None)
    assert '16/03/10 07:32' == col.renderCell(event)


def test_event__StartColumn__renderCell__2(DateTime, RequestFactory):
    """It renders only the date a whole-day event."""
    event = BaseEvent()
    event.datetime = DateTime(2016, 3, 10, 8, 32)
    event.whole_day_event = True
    col = StartColumn(None, RequestFactory(), None)
    assert '16/03/10' == col.renderCell(event)


def test_event__StartColumn__renderCell__3(DateTime, RequestFactory):
    """It returns en empty string if no `datetime` is set."""
    event = BaseEvent()
    col = StartColumn(None, RequestFactory(), None)
    assert '' == col.renderCell(event)


def test_event__Add__1(address_book, CategoryFactory, DateTime, browser):
    """It allows to add recurring events to the list."""
    CategoryFactory(address_book, 'birthday')
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_RECURRING_EVENTS_LIST_URL)
    browser.getLink(RECURRING_EVENT_ADD_TEXT).click()
    assert browser.CALENDAR_RECURRING_EVENT_ADD_URL == browser.url
    browser.getControl('event category').getControl('birthday').selected = True
    browser.getControl('date').value = DateTime.format_date(DateTime.now)
    browser.getControl('time').value = '21:45'
    browser.getControl('recurrence end').value = '2055 1 1 '
    browser.getControl(name='form.buttons.add').click()
    assert '"birthday" added.' == browser.message
    assert browser.CALENDAR_RECURRING_EVENTS_LIST_URL == browser.url
    browser.reload()  # get rid of the flash message
    # The new recurring event shows up in the list:
    assert 'birthday' in browser.contents


def test_event__Add__2(address_book, browser):
    """It is not accessible for a calendar visitor."""
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.CALENDAR_RECURRING_EVENT_ADD_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


def test_event__Edit__1(
        address_book, RecurringEventFactory, CategoryFactory, DateTime,
        browser):
    """It allows to edit a recurring event."""
    CategoryFactory(address_book, 'birthday')
    RecurringEventFactory(
        address_book, alternative_title='wedding day', datetime=DateTime.now,
        period='weekly')
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_RECURRING_EVENTS_LIST_URL)
    browser.getLink('wedding day').click()
    assert browser.CALENDAR_RECURRING_EVENT_EDIT_URL == browser.url
    assert 'wedding day' == browser.getControl('alternative title').value
    browser.getControl('alternative title').value = ''
    browser.getControl('event category').getControl('birthday').selected = True
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    # The changed event name shows up in the list:
    assert 'birthday' in browser.contents


def test_category__Edit__2(
        address_book, RecurringEventFactory, DateTime, browser):
    """It allows a calendar visitor only to see the recurring event data.

    But he cannot change or delete them.
    """
    RecurringEventFactory(
        address_book, alternative_title='foo', datetime=DateTime.now,
        period='weekly')
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_RECURRING_EVENT_EDIT_URL)
    # There are no fields and no delete button:
    assert (['form.buttons.apply', 'form.buttons.cancel'] ==
            browser.all_control_names)


def test_event__Delete__1(
        address_book, RecurringEventFactory, DateTime, browser):
    """It recurring_event_can_be_deleted."""
    RecurringEventFactory(
        address_book, alternative_title='birthday', datetime=DateTime.now)
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_RECURRING_EVENT_EDIT_URL)
    browser.getControl('Delete').click()
    assert browser.CALENDAR_RECURRING_EVENT_DELETE_URL == browser.url
    assert ('Do you really want to delete this recurring event?' in
            browser.contents)
    browser.getControl('Yes').click()
    assert '"birthday" deleted.' == browser.message


def test_category__Delete__2(
        address_book, RecurringEventFactory, DateTime, browser):
    """It is not accessible for a calendar visitor."""
    RecurringEventFactory(
        address_book, alternative_title='birthday', datetime=DateTime.now)
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.CALENDAR_RECURRING_EVENT_DELETE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)
