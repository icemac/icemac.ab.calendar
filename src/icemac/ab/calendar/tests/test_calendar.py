from gocept.month import Month
from icemac.ab.calendar.calendar import Calendar, CalendarDisplaySettings
from icemac.ab.calendar.event import get_event_data_from_recurring_event
from icemac.ab.calendar.interfaces import ICalendar, ICalendarDisplaySettings
from zope.interface.verify import verifyObject
import pytest
import pytz


def test_calendar__Calendar__1():
    """It fulfills the `ICalendar` interface."""
    assert verifyObject(ICalendar, Calendar())


def test_calendar__CalendarDisplaySettings__1():
    """It fulfills the `ICalendarDisplaySettings` interface."""
    assert verifyObject(ICalendarDisplaySettings, CalendarDisplaySettings())


@pytest.fixture('function')
def sample_events(address_book, CategoryFactory, EventFactory, DateTime):
    """Fixture providing some example events for tests."""
    foo = CategoryFactory(address_book, u'foo')
    bar = CategoryFactory(address_book, u'bar')
    # The order of creation is important to test that the results are sorted:
    EventFactory(address_book, alternative_title=u'start Mar 2013',
                 category=foo,
                 datetime=DateTime(2013, 3, 1, 0))
    EventFactory(address_book, alternative_title=u'start Feb 2013',
                 category=bar,
                 datetime=DateTime(2013, 2, 1, 0))
    EventFactory(address_book, alternative_title=u'end Jan 2013',
                 datetime=DateTime(2013, 1, 31, 23, 59))
    EventFactory(address_book, alternative_title=u'end Feb 2013',
                 category=foo,
                 datetime=DateTime(2013, 2, 28, 23, 59))
    return address_book


def test_calendar__Calendar__get_events_for_month__1(sample_events):
    """It returns only events in the given month."""
    assert ([u'start Feb 2013', u'end Feb 2013'] ==
            [x.alternative_title
             for x in sample_events.calendar.get_events_for_month(
                 Month(2, 2013))])


def test_calendar__Calendar__get_events_for_month__2(sample_events):
    """It respects the given time zone for an eastern time zone."""
    assert ([u'end Feb 2013', u'start Mar 2013'] ==
            [x.alternative_title
             for x in sample_events.calendar.get_events_for_month(
                 Month(2, 2013), 'Etc/GMT+1')])


def test_calendar__Calendar__get_events_for_month__3(sample_events):
    """It respects the given time zone for a western time zone."""
    assert ([u'end Jan 2013', u'start Feb 2013'] ==
            [x.alternative_title
             for x in sample_events.calendar.get_events_for_month(
                 Month(2, 2013), 'Etc/GMT-1')])


def test_calendar__Calendar__get_events_for_month__4(
        sample_events, address_book, RecurringEventFactory, CategoryFactory,
        DateTime):
    """It returns the recurring events in the given month."""
    RecurringEventFactory(
        address_book,
        alternative_title=u'each week',
        datetime=DateTime(2013, 2, 14, 23, 0),
        period=u'weekly',
        category=CategoryFactory(address_book, u'night lunch'))
    RecurringEventFactory(
        address_book,
        alternative_title=u'each week in future',
        datetime=DateTime(2013, 3, 1, 0),
        period=u'weekly',
        category=CategoryFactory(address_book, u'midnight'))
    assert ([(u'end Jan 2013', '2013-01-31T23:59:00+00:00'),
             (u'start Feb 2013', '2013-02-01T00:00:00+00:00'),
             (u'each week', '2013-02-15T00:00:00+01:00'),
             (u'each week', '2013-02-22T00:00:00+01:00')] ==
            [(x.alternative_title, x.datetime.isoformat())
             for x in address_book.calendar.get_events_for_month(
                 Month(2, 2013), 'Etc/GMT-1')])


def test_calendar__Calendar__get_events_for_month__5(
        address_book, CategoryFactory, RecurringEventFactory, EventFactory,
        DateTime):
    """A customized recurred event hides the original recurred event."""
    recurring_event = RecurringEventFactory(
        address_book,
        alternative_title=u'each week',
        datetime=DateTime(2013, 3, 14, 23, 0),
        period=u'weekly',
        category=CategoryFactory(address_book, u'night lunch'))
    event_data = get_event_data_from_recurring_event(
        recurring_event, DateTime(2013, 3, 21, 23, 0))
    event_data['alternative_title'] = u'this week'
    EventFactory(address_book, **event_data)
    assert ([(u'each week', '2013-03-14'),
             (u'this week', '2013-03-21'),
             (u'each week', '2013-03-28')] ==
            [(x.alternative_title, x.datetime.date().isoformat())
             for x in address_book.calendar.get_events_for_month(
                 Month(3, 2013), 'Etc/GMT+1')])


def test_calendar__Calendar__get_events_for_month__6(
        address_book, CategoryFactory, RecurringEventFactory, DateTime):
    """The recurring event with the higher prio in the category is rendered."""
    category = CategoryFactory(address_book, u'night lunch')
    RecurringEventFactory(
        address_book,
        alternative_title=u'monthly lunch',
        datetime=DateTime(2013, 3, 10, 12),
        period=u'nth weekday of month',
        category=category)
    RecurringEventFactory(
        address_book,
        alternative_title=u'weekly lunch',
        datetime=DateTime(2013, 3, 3, 12),
        period=u'weekly',
        category=category)
    assert ([(u'weekly lunch', '2013-03-03'),
             (u'monthly lunch', '2013-03-10'),
             (u'weekly lunch', '2013-03-17'),
             (u'weekly lunch', '2013-03-24'),
             (u'weekly lunch', '2013-03-31')] ==
            [(x.alternative_title, x.datetime.date().isoformat())
             for x in address_book.calendar.get_events_for_month(
                 Month(3, 2013), 'Etc/GMT+1')])


def test_calendar__Calendar__get_events_for_month__7(
        sample_events, address_book, EventFactory, DateTime):
    """It does not return deleted events."""
    event = EventFactory(
        address_book,
        alternative_title=u'deleted start of March 2013',
        datetime=DateTime(2013, 3, 1, 5))
    event.deleted = True
    assert ([u'start Mar 2013'] ==
            [x.alternative_title
             for x in address_book.calendar.get_events_for_month(
                 Month(3, 2013), 'Etc/GMT')])


def test_calendar__Calendar__get_events_for_month__8(
        address_book, EventFactory, DateTime):
    """A whole day event does not change the month via timezone."""
    EventFactory(address_book,
                 alternative_title=u'whole day',
                 datetime=DateTime(2015, 4, 30, 23),
                 whole_day_event=True)
    EventFactory(address_book,
                 alternative_title=u'day',
                 datetime=DateTime(2015, 4, 30, 23))
    assert ([u'whole day', u'day'] ==
            [x.alternative_title
             for x in address_book.calendar.get_events_for_month(
                 Month(4, 2015), 'Etc/GMT+8')])
    assert ([u'whole day'] ==
            [x.alternative_title
             for x in address_book.calendar.get_events_for_month(
                 Month(4, 2015), 'Etc/GMT-7')])


def test_calendar__Calendar__get_events_for_month__9(
        address_book, EventFactory, CategoryFactory, DateTime):
    """Deleted events are depressed in favour of not deleted ones.

    This behaviour requires the events to have the same category and the same
    time. It is needed to be able to delete a recurring event and add a new one
    later at the same place for the same category.
    """
    category = CategoryFactory(address_book, u'my cat')
    date = DateTime(2017, 5, 14, 13, 50, tzinfo=pytz.timezone('Europe/Berlin'))
    e1 = EventFactory(address_book, category=category, datetime=date)
    e1.deleted = True
    EventFactory(address_book, category=category, datetime=date)
    assert ([False] == [x.deleted
                        for x in address_book.calendar.get_events_for_month(
                            Month(5, 2017), 'Europe/Berlin')])


def test_calendar__Calendar__get_events__1(sample_events, DateTime):
    """It returns only events in the given time range."""
    assert ([u'end Jan 2013', u'start Feb 2013', u'end Feb 2013'] ==
            [x.alternative_title
             for x in sample_events.calendar.get_events(
                 DateTime(2013, 1, 30, 0), DateTime(2013, 3, 1, 0))])


def test_calendar__Calendar__get_events__2(sample_events, DateTime):
    """It returns only events for the given categories. (single category)"""
    assert ([u'end Feb 2013', u'start Mar 2013'] ==
            [x.alternative_title
             for x in sample_events.calendar.get_events(
                 DateTime(2013, 1, 1, 0), DateTime(2013, 3, 31, 0),
                 categories=['foo'])
             ])


def test_calendar__Calendar__get_events__3(
        sample_events, CategoryFactory, RecurringEventFactory, DateTime):
    """It returns only events for the given categories. (many categories)"""
    RecurringEventFactory(
        sample_events,
        category=CategoryFactory(sample_events, u'month'),
        alternative_title=u'each month',
        datetime=DateTime(2013, 2, 14, 23, 0),
        period=u'nth weekday of month')

    RecurringEventFactory(
        sample_events,
        category=CategoryFactory(sample_events, u'week'),
        alternative_title=u'each week',
        datetime=DateTime(2013, 1, 14, 23, 0),
        period=u'weekly')

    requested_categories = ['foo', 'bar', 'month']
    assert ([u'start Feb 2013',
             u'each month',
             u'end Feb 2013',
             u'start Mar 2013',
             u'each month',
             ] == [x.alternative_title
                   for x in sample_events.calendar.get_events(
                       DateTime(2013, 1, 1, 0), DateTime(2013, 3, 31, 0),
                       categories=requested_categories)])
