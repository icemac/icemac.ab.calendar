# -*- coding: utf-8 -*-
from datetime import timedelta, date
from icemac.ab.calendar.browser.calendar import EventDescription, hyphenated
from icemac.ab.calendar.browser.calendar import TabularCalendar
from icemac.ab.calendar.browser.interfaces import IEventDescription
from icemac.ab.calendar.browser.interfaces import UnknownLanguageError
from icemac.ab.calendar.event import Event
from icemac.ab.calendar.interfaces import ICalendarDisplaySettings, ICalendar
from icemac.ab.calendar.interfaces import IEvent, IRecurringEvent
from icemac.ab.calendar.testing import get_recurred_event
from icemac.addressbook.interfaces import IEntity
from mock import Mock, patch
from zope.interface.verify import verifyObject
from zope.preference.interfaces import IDefaultPreferenceProvider
from zope.security.interfaces import Unauthorized
from zope.testbrowser.browser import LinkNotFoundError
import pytest
import pytz
import zope.component


MONTH_FOR_TEST = 'November' if date.today().month == 5 else 'May'

# Helper functions


def set_event_additional_fields(address_book, *field_names):
    """Set the given fields to be displayed when an event is rendered."""
    event_entity = IEntity(IEvent)
    ICalendarDisplaySettings(address_book.calendar).event_additional_fields = [
        event_entity.getRawField(x)
        for x in field_names]


# Tests

def test_calendar__TabularCalendar__1(
        address_book, browser, EventFactory, DateTime):
    """It allows a visitor to access a filled calendar."""
    EventFactory(
        address_book, datetime=DateTime.now, alternative_title=u"Qwrtz")
    browser.login('cal-visitor')
    # We need to set a language as otherwise there will only be numbers
    # instead of week day names in the calendar:
    browser.lang('en')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert browser.CALENDAR_OVERVIEW_URL == browser.getLink('Calendar').url
    browser.getLink('Calendar').click()
    assert browser.CALENDAR_MONTH_OVERVIEW_URL == browser.url
    assert 'Sunday' in browser.contents
    assert 'Qwrtz' in browser.contents


def test_calendar__TabularCalendar__2(address_book, browser):
    """It allows a visitor to change his the time zone settings."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    browser.getLink('UTC').click()
    assert browser.PREFS_TIMEZONE_URL.startswith(browser.url)
    browser.getControl('Time zone').displayValue = ['Indian/Christmas']
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message


def test_calendar__TabularCalendar__3(address_book, browser):
    """It does not render an event add link for a visitor."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    # No link to add events:
    with pytest.raises(LinkNotFoundError):
        browser.getLink('event')


def test_calendar__TabularCalendar__4(address_book, browser):
    """It prevents access of anonymous."""
    browser.handleErrors = False  # needed to catch exception
    with pytest.raises(Unauthorized):
        browser.open(browser.CALENDAR_OVERVIEW_URL)


def test_calendar__TabularCalendar__selected_css_class__1(zcmlS):
    """It returns 'month' as selected if there is nothing in the session."""
    view = TabularCalendar()
    view.request = Mock()
    with patch('icemac.addressbook.browser.base.get_session') as session:
        session().get.return_value = None
        assert 'selected' == view.selected_css_class('month')
        assert None is view.selected_css_class('year')


def test_calendar__TabularCalendar__selected_css_class__2(zcmlS):
    """It returns the view stored in the session as selected."""
    view = TabularCalendar()
    view.request = Mock()
    with patch('icemac.addressbook.browser.base.get_session') as session:
        session().get.return_value = 'year'
        assert 'selected' == view.selected_css_class('year')
        assert None is view.selected_css_class('month')


def test_calendar__MonthSelectorForm__1(address_book, browser, DateTime):
    """It displays the current month by default."""
    browser.login('cal-visitor')
    # We need to explicitly set the language here because otherwise the
    # month name is not displayed:
    browser.lang('en')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    current_month = DateTime.now.strftime('%B')
    current_year = str(DateTime.now.year)
    assert [current_month] == browser.getControl('month').displayValue
    assert [current_year] == browser.getControl('year').displayValue


def test_calendar__MonthSelectorForm__2(address_book, browser):
    """It can switch to the entered month."""
    browser.login('cal-visitor')
    # We need to explicitly set the language here because otherwise the
    # month name is not displayed:
    browser.lang('en')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    browser.getControl('month').getControl(MONTH_FOR_TEST).click()
    browser.getControl('year').getControl('2024').click()
    browser.getControl('Apply').click()
    assert 'Month changed.' == browser.message
    assert [MONTH_FOR_TEST] == browser.getControl('month').displayValue
    assert ['2024'] == browser.getControl('year').displayValue


def test_calendar__MonthSelectorForm__3(address_book, browser):
    """It keeps the month the user switched to."""
    browser.login('cal-visitor')
    # We need to explicitly set the language here because otherwise the
    # month name is not displayed:
    browser.lang('en')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    browser.getControl('month').getControl(MONTH_FOR_TEST).click()
    browser.getControl('year').getControl('2024').click()
    browser.getControl('Apply').click()
    assert 'Month changed.' == browser.message
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    assert [MONTH_FOR_TEST] == browser.getControl('month').displayValue
    assert ['2024'] == browser.getControl('year').displayValue


def test_calendar__MonthSelectorForm__4(address_book, browser):
    """It translates the months in the month dropdown."""
    browser.login('cal-visitor')
    browser.lang('de-DE')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    assert 'Mai' == browser.getControl('month').displayOptions[4]


def test_calendar__Dispatcher__1(address_book, browser):
    """It keeps the view mode switched to."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    browser.getLink('Year').click()
    assert browser.CALENDAR_YEAR_OVERVIEW_URL == browser.url
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    assert browser.CALENDAR_YEAR_OVERVIEW_URL == browser.url


def test_calendar__MonthCalendar__1(
        address_book, EventFactory, DateTime, browser):
    """It shows the events belonging to the selected month."""
    now = DateTime.now
    EventFactory(address_book, alternative_title=u'foo bär', datetime=now)
    EventFactory(address_book, alternative_title=u'baz qux',
                 datetime=now + timedelta(days=31))
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    assert 'foo bär' in browser.contents
    assert 'baz qux' not in browser.contents


def test_calendar__MonthCalendar__2(
        address_book, RecurringEventFactory, CategoryFactory, DateTime,
        browser):
    """It shows recurred events as links to customize them."""
    RecurringEventFactory(
        address_book, alternative_title=u'foo bär', datetime=DateTime.now,
        period=u'weekly', category=CategoryFactory(address_book, u'bat'))
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    assert browser.getLink(u'foo bär').url.startswith(
        browser.RECURRED_EVENT_CUSTOMIZE_URL)
    assert browser.getLink(u'foo bär').url.endswith(
        '@@customize-recurred-event?date={}&event=RecurringEvent'.format(
            date.today().isoformat()))


def test_calendar__MonthCalendar__3(address_book, browser):
    """It renders the time zone the user has set in the prefs as a link."""
    default_prefs = zope.component.getUtility(IDefaultPreferenceProvider)
    default_prefs.getDefaultPreferenceGroup(
        'ab.timeZone').time_zone = 'Pacific/Fiji'
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    assert browser.PREFS_TIMEZONE_URL.startswith(
        browser.getLink('Pacific/Fiji').url)


def test_calendar__MonthCalendar__4(
        address_book, EventFactory, DateTime, browser):
    """It shows events in the time zone selected by the user."""
    default_prefs = zope.component.getUtility(IDefaultPreferenceProvider)
    default_prefs.getDefaultPreferenceGroup(
        'ab.timeZone').time_zone = 'America/Los_Angeles'
    EventFactory(address_book, alternative_title=u'1st of april utc',
                 datetime=DateTime(2014, 4, 1, 0))
    EventFactory(address_book, alternative_title=u'2nd of april utc',
                 datetime=DateTime(2014, 4, 2, 0))
    browser.login('cal-visitor')
    # We need to explicitly set the language here because otherwise the month
    # name is not displayed:
    browser.lang('en')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    browser.getControl('month').getControl('April').selected = True
    browser.getControl('year').getControl('2014').selected = True
    browser.getControl('Apply').click()
    assert 'Month changed.' == browser.message
    # 1st of april 0:00 UTC is in march for Los Angeles timezone, so it
    # does not show up here.
    assert '1st of april utc' not in browser.contents
    assert '2nd of april utc' in browser.contents


def test_calendar__MonthCalendar__5(address_book, browser):
    """It can switch to the year view."""
    browser.login('cal-visitor')
    # We need to explicitly set the language here because otherwise the month
    # names are not displayed:
    browser.lang('en')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    browser.getLink('Year').click()
    assert browser.CALENDAR_YEAR_OVERVIEW_URL == browser.url
    year = date.today().year
    assert 'January {}'.format(year) in browser.contents
    assert 'December {}'.format(year) in browser.contents


def test_calendar__MonthCalendar__6(
        address_book, FieldFactory, CategoryFactory, DateTime,
        RecurringEventFactory, browser):
    """It displays the fields of event objects selected in master data."""
    # Create user fields for select
    event_field_name = FieldFactory(
        address_book, IEvent, u'Int', u'reservations').__name__
    revent_field_name = FieldFactory(
        address_book, IRecurringEvent, u'Int', u'reservations').__name__
    # Sort order is used for display in calendar:
    set_event_additional_fields(
        address_book, 'text', event_field_name, 'persons')

    category = CategoryFactory(address_book, u'bar')
    data = {'datetime': DateTime.now, 'text': u'Text1',
            'period': 'yearly', revent_field_name: 42,
            'external_persons': [u'Ben Utzer'], 'category': category}
    RecurringEventFactory(address_book, **data)
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    assert [
        'Text1',
        '42',
        'Ben Utzer'
    ] == browser.etree.xpath('//ul[@class="info"]/li/text()')


@pytest.mark.webdriver
def test_calendar__MonthCalendar__7_webdriver(address_book, webdriver):
    """It renders previous and next links switching months."""
    cal = webdriver.calendar
    webdriver.login('cal-visitor', cal.CALENDAR_MONTH_OVERVIEW_URL)
    cal.year = 2026
    cal.month = 'January'
    cal.switch_to_previous_month()
    assert 'December' == cal.month
    assert 2025 == cal.year
    cal.switch_to_next_month()
    cal.switch_to_next_month()
    assert 'February' == cal.month
    assert 2026 == cal.year


def test_calendar__YearCalendar__1(
        address_book, EventFactory, DateTime, browser):
    """It shows the events belonging to the selected year."""
    now = DateTime.now
    EventFactory(address_book, alternative_title=u'this year', datetime=now)
    EventFactory(address_book, alternative_title=u'next year',
                 datetime=now + timedelta(days=366))
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_YEAR_OVERVIEW_URL)
    assert 'this year' in browser.contents
    assert 'next year' not in browser.contents


def test_calendar__YearCalendar__2(
        address_book, RecurringEventFactory, TimeZonePrefFactory, DateTime,
        CategoryFactory, browser):
    """It renders events with a constant time even through DST changes."""
    TimeZonePrefFactory('Europe/Berlin')
    RecurringEventFactory(
        address_book,
        datetime=DateTime(
            2014, 3, 11, 8, tzinfo=pytz.timezone('Europe/Berlin')),
        end=DateTime(2014, 5, 2).date(),
        category=CategoryFactory(address_book, u'my cat'),
        period='nth weekday of month')
    browser.login('cal-visitor')
    # We need to explicitly set the language here because otherwise the month
    # name is not displayed:
    browser.lang('en')
    browser.open(browser.CALENDAR_YEAR_OVERVIEW_URL)
    browser.getControl('year').getControl('2014').selected = True
    browser.handleErrors = False
    browser.getControl('Apply').click()
    assert 'Year changed.' == browser.message
    # The time stays the same even there is a DST switch in between:
    assert ['8:00 AM', '8:00 AM'] == browser.etree.xpath('//table//dt/text()')


@pytest.mark.webdriver
def test_calendar_js__1_webdriver(address_book, webdriver):
    """It auto-submits on change in the month drop-down of the month view."""
    calendar = webdriver.calendar
    webdriver.login('cal-visitor', calendar.CALENDAR_MONTH_OVERVIEW_URL)
    calendar.month = MONTH_FOR_TEST
    assert u'Month changed.' == webdriver.message


@pytest.mark.webdriver
def test_calendar_js__2_webdriver(address_book, webdriver):
    """It auto-submits on change in the year drop-down of the month view."""
    calendar = webdriver.calendar
    webdriver.login('cal-visitor', calendar.CALENDAR_MONTH_OVERVIEW_URL)
    calendar.year = 2024
    assert u'Month changed.' == webdriver.message


@pytest.mark.webdriver
def test_calendar_js__3_webdriver(address_book, webdriver):
    """It auto-submits on change in the year drop-down of the year view."""
    calendar = webdriver.calendar
    webdriver.login('cal-visitor', calendar.CALENDAR_YEAR_OVERVIEW_URL)
    calendar.year = 2024
    assert u'Year changed.' == webdriver.message


def test_calendar__EventDescription__1(EventDescriptionFactory):
    """It fulfills the `IEventDescription` interface."""
    event_description = EventDescriptionFactory(Event())
    assert isinstance(event_description, EventDescription)
    assert verifyObject(IEventDescription, event_description)


def test_calendar__EventDescription__persons__1(
        address_book, PersonFactory, EventFactory, EventDescriptionFactory):
    """It is a comma separated list of persons.

    It combines the persons from the address book and the external persons.
    """
    person = PersonFactory(address_book, u'Tester', first_name=u'Hans')
    event = EventFactory(
        address_book, persons=set([person]), external_persons=[u'Heiner Myer'])
    event_description = EventDescriptionFactory(event=event)
    assert u'Hans Tester, Heiner Myer' == event_description.persons


def test_calendar__EventDescription__persons__2(EventDescriptionFactory):
    """It is an empty string if there are no persons assigned to the event."""
    assert u'' == EventDescriptionFactory(Event()).persons


@pytest.fixture('function')
def selected_user_field(address_book, FieldFactory):
    """Create a user defined field ad select it for display.

    Return the name of the user defined field.
    """
    field_name = FieldFactory(
        address_book, IEvent, u'Int', u'reservations').__name__
    set_event_additional_fields(address_book, 'text', field_name)
    return field_name


def test_calendar__EventDescription__getInfo__1(
        address_book, CategoryFactory, RecurringEventFactory, DateTime,
        selected_user_field, utc_time_zone_pref):
    """It ignores not existing fields.

    This happens if a user defined field is chosen for display but there is no
    equivalent field on the recurring event which is rendered as recurred
    event.

    """
    recurring_event = RecurringEventFactory(address_book, **{
        'datetime': DateTime.now,
        'text': u'Text2',
        'period': 'daily',
        'category': CategoryFactory(address_book, u'bar')})
    ed = IEventDescription(get_recurred_event(recurring_event, DateTime))
    assert ['Text2'] == ed.getInfo()


def test_calendar__EventDescription__getInfo__2(
        address_book, EventFactory, DateTime, CategoryFactory,
        selected_user_field, utc_time_zone_pref):
    """It ignores a selected but later deleted user defined field."""
    ed = IEventDescription(EventFactory(address_book, **{
        'datetime': DateTime.now,
        'text': u'Text1',
        'category': CategoryFactory(address_book, u'bar'),
        selected_user_field: 42}))
    event_entity = IEntity(IEvent)
    event_entity.removeField(event_entity.getRawField(selected_user_field))
    assert ['Text1'] == ed.getInfo()


def test_calendar__EventDescription__getInfo__3(
        address_book, FieldFactory, EventFactory, utc_time_zone_pref):
    """It returns a list of the selected fields as unicode objects."""
    reservations = FieldFactory(
        address_book, IEvent, u'Int', u'reservations').__name__
    # Both user fields and pre-defined fields are possible
    set_event_additional_fields(address_book, 'text', reservations)
    ed = IEventDescription(EventFactory(address_book, **{
        'text': u'Event is not yet sure.',
        reservations: 50}))
    assert [u'Event is not yet sure.', u'50'] == ed.getInfo()


def test_calendar__EventDescription__getInfo__4(
        address_book, EventFactory, utc_time_zone_pref):
    """It splits the text field at line endings."""
    set_event_additional_fields(address_book, 'text')
    ed = IEventDescription(EventFactory(address_book, text=u'foo\nbar'))
    assert [u'foo', u'bar'] == ed.getInfo()


def test_calendar__EventDescription__getInfo__5(
        address_book, EventFactory, utc_time_zone_pref):
    """It omits fields with a `None` value."""
    set_event_additional_fields(address_book, 'text')
    ed = IEventDescription(EventFactory(address_book))
    assert ed.context.text is None
    assert [] == ed.getInfo()


def test_calendar__EventDescription__getInfo__6(
        address_book, EventFactory, utc_time_zone_pref):
    """It omits empty string values."""
    set_event_additional_fields(address_book, 'persons')
    ed = IEventDescription(EventFactory(address_book))
    assert '' == ed.persons
    assert [] == ed.getInfo()


def test_calendar__EventDescription__getInfo__7(
        address_book, FieldFactory, EventFactory, utc_time_zone_pref):
    """It does not omit numbers with the value of zero."""
    num_field = FieldFactory(address_book, IEvent, u'Int', u'num').__name__
    set_event_additional_fields(address_book, num_field)
    ed = IEventDescription(EventFactory(address_book, **{num_field: 0}))
    assert [u'0'] == ed.getInfo()


def test_calendar__EventDescription__getInfo__8(
        address_book, PersonFactory, EventFactory, utc_time_zone_pref):
    """It returns external and internal persons if `persons` is  selected."""
    p1 = PersonFactory(address_book, u'Tester', first_name=u'Hans')
    set_event_additional_fields(address_book, 'persons')
    ed = IEventDescription(EventFactory(
        address_book,
        persons=set([p1]),
        external_persons=[u'Franz Vrozzek', u'Fritz Vrba']))
    assert [u'Franz Vrozzek, Fritz Vrba, Hans Tester'] == ed.getInfo()


def test_calendar__EventDescription__getInfo__9(
        address_book, EventFactory, utc_time_zone_pref):
    """It hyphenates the text."""
    set_event_additional_fields(address_book, 'text')
    ed = IEventDescription(EventFactory(
        address_book, text=u'I contain longer words.'))
    assert [u'I con&shy;tain longer word&shy;s.'] == ed.getInfo(lang='en')


def test_calendar__EventDescription__getText__1(EventDescriptionFactory):
    """It returns the alternative title if it is set."""
    ed = EventDescriptionFactory(
        Event(), category_name=u'birthday', alternative_title=u'foo bar')
    assert u'foo bar' == ed.getText()


def test_calendar__EventDescription__getText__2(
        address_book, EventDescriptionFactory, CategoryFactory):
    """It returns the category title if the alternative title is not set."""
    ed = EventDescriptionFactory(
        Event(), category=CategoryFactory(address_book, u'foo'),
        alternative_title=None)
    assert u'foo' == ed.getText()


def test_calendar__EventDescription__getText__3(EventDescriptionFactory):
    """It returns 'event' if neither alternative title nor category is set."""
    ed = EventDescriptionFactory(
        Event(), category=None, alternative_title=None)
    assert u'event' == ed.getText()


def test_calendar__EventDescription__getText__4(EventDescriptionFactory):
    """It returns not hyphenated text by default."""
    ed = EventDescriptionFactory(Event(), alternative_title=u'birthday')
    assert u'birthday' == ed.getText()


def test_calendar__EventDescription__getText__5(EventDescriptionFactory):
    """It raises `UnknownLanguageError` for an unknown language."""
    ed = EventDescriptionFactory(Event())
    with pytest.raises(UnknownLanguageError):
        ed.getText(lang='Clingon')


def test_calendar__EventDescription__getText__6(EventDescriptionFactory):
    """getText_returns_hyphenated_respecting_set_language."""
    ed = EventDescriptionFactory(Event(), alternative_title=u'Geburtstag')
    assert u'Ge&shy;burts&shy;tag' == ed.getText(lang='de')


def test_calendar__hyphenated__1():
    """It quotes text as html even if not hyphenating when no lang is set."""
    @hyphenated
    def func(ignored):
        return u'<script>'
    assert u'&lt;script&gt;' == func(any)


def test_calendar__hyphenated__2():
    """It hyphenates text and encodes it text for html."""
    @hyphenated
    def func(ignored, lang=None):
        return u'Gebürtstag<>'

    res = func(any, lang='de')
    assert isinstance(res, unicode)
    assert u'Ge&shy;bürts&shy;tag&lt;&gt;' == res


def test_calendar__calendar_for_event_description__1(
        address_book, EventFactory, EventDescriptionFactory):
    """It adapts IEventDescription to ICalendar."""
    ed = EventDescriptionFactory(EventFactory(address_book))
    assert address_book.calendar == ICalendar(ed)


def test_calendar__event_for_event_description__1(
        address_book, EventFactory, EventDescriptionFactory):
    """It adapts IEventDescription to IEvent."""
    event = EventFactory(address_book)
    ed = EventDescriptionFactory(event)
    assert event == IEvent(ed)
