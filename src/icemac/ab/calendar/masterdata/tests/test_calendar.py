from icemac.ab.calendar.interfaces import IEvent
from icemac.addressbook.interfaces import IEntity
from zope.testbrowser.browser import LinkNotFoundError
import pytest
import zope.component.hooks


def test_calendar__CalendarView__1(address_book, FieldFactory, browser):
    """It allows to select fields for display in the calendar."""
    field = FieldFactory(
        address_book, IEvent, u'Int', u'reservations').__name__
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    browser.getLink('Calendar view').click()
    assert browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL == browser.url
    browser.getControl('Additional event fields').displayValue = [
        'persons',
        'reservations',
    ]
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL)
    assert browser.getControl('Additional event fields').displayValue == [
        'persons',
        'reservations',
    ]
    # It does not break on selected but deleted user defined field:
    with zope.component.hooks.site(address_book):
        event_entity = IEntity(IEvent)
        event_entity.removeField(event_entity.getRawField(field))
    browser.open(browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL)
    assert browser.getControl('Additional event fields').displayValue == [
        'persons',
    ]


def test_calendar__CalendarView__2(address_book, browser):
    """It is not shown on calendar master data for a calendar visitor."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('Calendar view')


def test_calendar__CalendarView__3(address_book, browser):
    """It is not accessible for a calendar visitor."""
    browser.login('cal-visitor')
    browser.assert_forbidden(browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL)


def test_calendar__CalendarCounts__1(address_book, browser):
    """It is accessible via calendar master data."""
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    browser.getLink('Event counts').click()
    assert browser.url == browser.CALENDAR_EVENTCOUNTS


def test_calendar__CalendarCounts__2(address_book, browser):
    """It renders a message if there are no events in the calendar at all."""
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_EVENTCOUNTS)
    assert 'No event events created in any year.' in browser.contents


def test_calendar__CalendarCounts__3(
        address_book, browser, RecurringEventFactory):
    """It renders the number of created recurring events."""
    RecurringEventFactory(address_book)
    RecurringEventFactory(address_book)
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_EVENTCOUNTS)

    assert '>recurring event<' in browser.contents
    assert '>(all years)<' in browser.contents
    assert '<td>2</td>' in browser.contents


def test_calendar__CalendarCounts__4(
        address_book, browser, EventFactory, DateTime):
    """It renders the number of created events per year."""
    EventFactory(address_book, datetime=DateTime(2020, 4, 13, 17))
    EventFactory(address_book, datetime=DateTime(2020, 2, 29, 17))
    EventFactory(address_book, datetime=DateTime(2019, 12, 31, 17))
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_EVENTCOUNTS)

    assert '>event<' in browser.contents
    assert '>2020<' in browser.contents
    assert '>2<' in browser.contents
    assert '>2019<' in browser.contents
    assert '>1<' in browser.contents
