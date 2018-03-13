from __future__ import unicode_literals
import mock


def test_browser__EventView__1(
        address_book, EventViewConfigurationFactory, EventFactory,
        CategoryFactory, RecurringEventFactory, DateTime, browser):
    """It renders a listing of event views."""
    EventFactory(
        address_book, category=CategoryFactory(address_book, 'Party'),
        datetime=DateTime.now)
    RecurringEventFactory(
        address_book, category=CategoryFactory(address_book, 'Lesson'),
        datetime=DateTime.add(DateTime.now, days=3),
        period='weekly')
    EventViewConfigurationFactory(
        address_book, '-1 day for 1 week', start=-1, duration=7)

    browser.login('cal-visitor')
    browser.lang(b'en')
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    browser.getLink('Event views').click()
    assert browser.CALENDAR_EVENT_VIEWS_URL == browser.url
    assert '>Party<' in browser.ucontents
    assert '>Lesson<' in browser.ucontents


def test_browser__EventView__2(
        address_book, EventViewConfigurationFactory, DateTime, browser):
    """It renders a month headline only if days in this month are rendered."""
    EventViewConfigurationFactory(
        address_book, '1 week', start=0, duration=7)

    with mock.patch('icemac.ab.calendar.eventview.browser.date') as date:
        date.today.return_value = DateTime(2018, 2, 21).date()
        browser.login('cal-visitor')
        browser.lang(b'en')
        browser.open(browser.CALENDAR_EVENT_VIEWS_URL)
    assert 'February 2018' in browser.ucontents
    assert 'March 2018' not in browser.ucontents


def test_browser__EventView__3(
        address_book, EventViewConfigurationFactory, DateTime, browser):
    """It renders sundays with a special css class."""
    EventViewConfigurationFactory(
        address_book, '1 week', start=0, duration=7)

    with mock.patch('icemac.ab.calendar.eventview.browser.date') as date:
        date.today.return_value = DateTime(2018, 2, 21).date()
        browser.login('cal-visitor')
        browser.lang(b'en')
        browser.open(browser.CALENDAR_EVENT_VIEWS_URL)
    assert ' bg-warning">Sunday, 25.<' in browser.ucontents


def test_browser__EventView__4(
        address_book, EventViewConfigurationFactory, DateTime, browser):
    """It allows to select a different event view config."""
    EventViewConfigurationFactory(address_book, '1 week', start=0, duration=7)
    EventViewConfigurationFactory(
        address_book, '2 weeks', start=0, duration=14)

    with mock.patch('icemac.ab.calendar.eventview.browser.date') as date:
        date.today.return_value = DateTime(2018, 2, 21).date()
        browser.login('cal-visitor')
        browser.lang(b'en')
        browser.open(browser.CALENDAR_EVENT_VIEWS_URL)
        assert 'March 2018' not in browser.ucontents

        browser.getControl(name='views:list').displayValue = ['2 weeks']
        browser.getForm().submit()
        assert 'March 2018' in browser.ucontents


def test_browser__EventView__5(
        address_book, EventViewConfigurationFactory, DateTime, browser):
    """It renders the current day specially."""
    EventViewConfigurationFactory(address_book, '1 week', start=-1, duration=7)

    with mock.patch('icemac.ab.calendar.eventview.browser.date') as date:
        date.today.return_value = DateTime(2018, 2, 21).date()
        browser.login('cal-visitor')
        browser.lang(b'en')
        browser.open(browser.CALENDAR_EVENT_VIEWS_URL)
        assert 'text-success">Wednesday, 21.<' in browser.ucontents


def test_browser__EventView__6(
        address_book, EventViewConfigurationFactory, EventFactory,
        CategoryFactory, RecurringEventFactory, DateTime, browser):
    """It filters the events by the selected categories."""
    party = CategoryFactory(address_book, 'Party')
    EventFactory(address_book, category=party, datetime=DateTime.now)
    RecurringEventFactory(
        address_book, category=CategoryFactory(address_book, 'Lesson'),
        datetime=DateTime.add(DateTime.now, days=3),
        period='weekly')
    EventViewConfigurationFactory(
        address_book, '-1 day for 1 week', start=-1, duration=7,
        categories=set([party]))

    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_EVENT_VIEWS_URL)
    assert '>Party<' in browser.ucontents
    assert '>Lesson<' not in browser.ucontents