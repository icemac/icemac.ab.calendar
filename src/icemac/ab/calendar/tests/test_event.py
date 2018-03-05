from gocept.reference.verify import verifyObject
from icemac.ab.calendar.event import BaseEvent, Event, RecurredEvent
from icemac.ab.calendar.event import RecurringEvent, RecurringEventContainer
from icemac.ab.calendar.event import _get_field_name_on_IEvent
from icemac.ab.calendar.event import get_event_data_from_recurring_event
from icemac.ab.calendar.interfaces import IEvent, IEventDateTime, ICalendar
from icemac.ab.calendar.interfaces import IRecurredEvent, DATE_INDEX
from icemac.ab.calendar.interfaces import IRecurringEvent, IRecurringEvents
from icemac.addressbook.interfaces import IEntity, ITitle, ISchemaName
import pytz
import zope.catalog.interfaces
import zope.component


def test_event__BaseEvent__listPersons__1(address_book, PersonFactory):
    """It returns a list of persons in the address book and externals."""
    event = BaseEvent()
    event.persons = set([
        PersonFactory(address_book, u'Tester', first_name=u'Hans'),
        PersonFactory(address_book, u'Koch', first_name=u'Fritz')])
    event.external_persons = [u'Klaus Arkpe', u'Heiner Myer']
    assert ([u'Fritz Koch', u'Hans Tester', u'Heiner Myer', u'Klaus Arkpe'] ==
            event.listPersons())


def test_event__BaseEvent__in_timezone__1(DateTime):
    """It returns a whole day event as midnight of the given time zone."""
    tz = pytz.timezone('Europe/Berlin')
    event = BaseEvent()
    event.whole_day_event = True
    event.datetime = DateTime(2015, 1, 5, 13, 13)
    assert DateTime(2015, 1, 5, 0, tzinfo=tz) == event.in_timezone(tz)


def test_event__BaseEvent__in_timezone__2(DateTime):
    """It returns the datetime of a non-whole-day event in given time zone."""
    tz = pytz.timezone('Europe/Berlin')
    event = BaseEvent()
    event.whole_day_event = False
    event.datetime = DateTime(2015, 1, 5, 10)  # UTC
    assert tz.normalize(DateTime(2015, 1, 5, 10)) == event.in_timezone(tz)


def test_event__Event__1(zcmlS):
    """It implements the `IEvent` interface."""
    assert verifyObject(IEvent, Event())


def test_event__Event__2(
        address_book, FullPersonFactory, EventFactory, browser):
    """A person referenced on an event can still become a principal."""
    person = FullPersonFactory(
        address_book, u'Tester', email__email=u'tester@example.com')
    EventFactory(address_book, persons=set([person]))
    browser.login('mgr')
    browser.open(browser.PRINCIPAL_ADD_URL)
    # A user referenced on an event is still in the list of persons which
    # might become a principal:
    assert ['Tester'] == browser.getControl('person').displayOptions


def test_event__Event__3(address_book, CategoryFactory, DateTime, browser):
    """A new field can be added to it and it can be used."""
    CategoryFactory(address_book, u'Wedding')
    browser.login('mgr')
    browser.open(browser.ENTITIES_EDIT_URL)
    # It is possible to a a new field to an event:
    browser.getLink('Edit fields', index=8).click()
    assert browser.CALENDAR_EVENT_FIELDS_LIST_URL == browser.url
    browser.getLink('field').click()
    browser.getControl('type').displayValue = ['integer number']
    browser.getControl('title').value = 'Number of reservations'
    browser.getControl('Add', index=1).click()
    assert '"Number of reservations" added.' == browser.message
    # This new field can be used in the event add form:
    browser.open(browser.EVENT_ADD_URL)
    browser.getControl('date').value = DateTime.format_date(DateTime.now)
    browser.getControl('yes').selected = True  # whole day event?
    browser.getControl('event category').displayValue = ['Wedding']
    browser.getControl('Number of reservations').value = '42'
    browser.getControl('Add', index=1).click()
    assert '"Wedding" added.' == browser.message
    # and it can be used in the event edit form:
    browser.open(browser.EVENT_EDIT_URL)
    assert '42' == browser.getControl('Number of reservations').value
    browser.getControl('Number of reservations').value = '41'
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message


def test_event__Event____repr____1(zcmlS, DateTime):
    """It returns some data of the event."""
    event = Event()
    event.datetime = DateTime(2016, 4, 6, 16)
    event.alternative_title = u'my-title'
    assert (
        "<Event datetime='2016-04-06 16:00:00+00:00' title=u'my-title', "
        "deleted=False>" == repr(event))


def test_event__Event__schema__1(zcmlS):
    """It can be adapted to ``ISchemaName``."""
    assert 'IEvent' == ISchemaName(Event()).schema_name


def test_event__RecurringEventContainer__1():
    """It implements the `IRecurringEvents` interface."""
    assert verifyObject(IRecurringEvents, RecurringEventContainer())


def test_event__RecurringEventContainer__get_events__1(
        address_book, RecurringEventFactory, DateTime):
    """It sorts the events by their weights."""
    RecurringEventFactory(
        address_book,
        datetime=DateTime.now,
        alternative_title=u'weekly',
        period='weekly')
    RecurringEventFactory(
        address_book,
        datetime=DateTime.now,
        alternative_title=u'yearly',
        period='yearly')
    RecurringEventFactory(
        address_book,
        datetime=DateTime.now,
        alternative_title=u'biweekly',
        period='biweekly')
    RecurringEventFactory(
        address_book,
        datetime=DateTime.now,
        alternative_title=u'nth weekday of month',
        period='nth weekday of month')
    recurring_events = zope.component.getUtility(IRecurringEvents)
    assert ([u'weekly', u'biweekly', u'nth weekday of month', u'yearly'] ==
            [x.alternative_title for x in recurring_events.get_events([])])


def test_event__RecurringEvent__1(zcmlS, DateTime):
    """It implements the `IRecurringEvent` interface."""
    revent = RecurringEvent()
    revent.datetime = DateTime.now
    revent.period = u'weekly'
    assert verifyObject(IRecurringEvent, revent)


def test_event__RecurringEvent____repr____1(zcmlS, DateTime):
    """It returns some data of the recurring event."""
    event = RecurringEvent()
    event.datetime = DateTime(2016, 4, 6, 16)
    event.alternative_title = u'my-rec-title'
    assert (
        "<RecurringEvent datetime='2016-04-06 16:00:00+00:00' "
        "title=u'my-rec-title', deleted=False>" == repr(event))


def test_event__RecurringEvent__schema__1(zcmlS):
    """It can be adapted to ``ISchemaName``."""
    assert 'IRecurringEvent' == ISchemaName(RecurringEvent()).schema_name


def test_event__RecurringEvent__get_events__1(
        address_book, RecurringEventFactory, CategoryFactory, DateTime):
    """It returns an iterable of `RecurredEvent` instances."""
    recurring_event = RecurringEventFactory(
        address_book,
        datetime=DateTime(2014, 5, 2, 12),
        text=u'foobar',
        period='weekly',
        category=CategoryFactory(address_book, u'birthday'))
    events = list(recurring_event.get_events(
        DateTime(2014, 5, 1, 0), DateTime(2014, 5, 8, 0), pytz.utc))
    assert 1 == len(events)
    event = events[0]
    assert isinstance(event, RecurredEvent)
    assert 'foobar' == event.text


def test_event__RecurringEvent__get_events__2(
        address_book, RecurringEventFactory, CategoryFactory, DateTime):
    """It ends the recurrence at the `end` date."""
    recurring_event = RecurringEventFactory(
        address_book,
        datetime=DateTime(2014, 4, 18, 12),
        end=DateTime(2014, 5, 9, 0).date(),
        period='weekly',
        category=CategoryFactory(address_book, u'event'))
    events = list(recurring_event.get_events(
        DateTime(2014, 5, 1, 0), DateTime(2014, 5, 31, 0), pytz.utc))
    assert 2 == len(events)
    assert ([DateTime(2014, 5, 2, 12),
             DateTime(2014, 5, 9, 12)] == [x.datetime for x in events])

    # If the end date is not reached all recurrences until the requested
    # interval end are returned:
    events = list(recurring_event.get_events(
        DateTime(2014, 4, 1, 0), DateTime(2014, 4, 30, 0), pytz.utc))
    assert 2 == len(events)
    assert ([DateTime(2014, 4, 18, 12),
             DateTime(2014, 4, 25, 12)] == [x.datetime for x in events])


def test_event__RecurringEvent__get_events__3(
        address_book, RecurringEventFactory, CategoryFactory, DateTime):
    """The local time of the recurred event does not change in DST.

    DST ... daylight saving time
    """
    recurring_event = RecurringEventFactory(
        address_book,
        datetime=DateTime(2016, 3, 24, 12),
        period='weekly',
        category=CategoryFactory(address_book, u'event'))
    tz_berlin = pytz.timezone('Europe/Berlin')
    # At 2016-03-27 DST starts in Europe/Berlin
    events = list(recurring_event.get_events(
        DateTime(2016, 3, 24, 0), DateTime(2016, 4, 1, 0), tz_berlin))
    assert ([DateTime(2016, 3, 24, 13, tzinfo=tz_berlin),
             DateTime(2016, 3, 31, 13, tzinfo=tz_berlin)] ==
            [x.datetime for x in events])
    # So the time in UTC changes to keep it the same in local time:
    assert ([DateTime(2016, 3, 24, 12),
             DateTime(2016, 3, 31, 11)] ==
            [pytz.utc.normalize(x.datetime) for x in events])


def test_event__RecurredEvent__create_from__1(
        address_book, FieldFactory, RecurringEventFactory, CategoryFactory,
        PersonFactory, DateTime):
    """It copies attributes from the given parameters."""
    event_field_name = FieldFactory(
        address_book, IEvent, u'Int', u'reserve').__name__
    revent_field = FieldFactory(
        address_book, IRecurringEvent, u'Int', u'reserve').__name__
    data = {
        'datetime': DateTime(2014, 5, 2, 12),
        'category': CategoryFactory(address_book, u'birthday'),
        'period': 'weekly',
        'persons': set([PersonFactory(address_book, u'Tester')]),
        revent_field: 42}
    recurring_event = RecurringEventFactory(address_book, **data)

    recurred_event = RecurredEvent.create_from(
        recurring_event, DateTime(2014, 4, 12, 21))
    assert DateTime(2014, 4, 12, 21) == recurred_event.datetime
    assert list(recurring_event.persons)[0] in recurred_event.persons
    assert recurring_event.category == recurred_event.category
    assert address_book.calendar == recurred_event.__parent__
    assert recurring_event == recurred_event.recurring_event
    assert 42 == getattr(recurred_event, event_field_name)


def test_event__RecurringEvent__2(
        address_book, EventFactory, RecurringEventFactory, DateTime):
    """It does not get catalogued but only Event objects."""
    dt = DateTime.now
    event = EventFactory(address_book, datetime=dt)
    RecurringEventFactory(address_book, datetime=dt, period='weekly')
    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    results = catalog.searchResults(**{DATE_INDEX: {'any': None}})
    assert [event] == list(results)


def test_event__RecurredEvent__1():
    """It implements the `IRecurredEvent` interface."""
    assert verifyObject(IRecurredEvent, RecurredEvent())


def test_event__RecurredEvent____repr____1(
        address_book, CategoryFactory, RecurringEventFactory, DateTime):
    """It returns some data of the recurred event."""
    recurring_event = RecurringEventFactory(
        address_book,
        datetime=DateTime(2014, 5, 2, 12),
        period='weekly',
        category=CategoryFactory(address_book, u'birthday'))
    events = list(recurring_event.get_events(
        DateTime(2014, 5, 1, 0), DateTime(2014, 5, 8, 0), pytz.utc))
    recurred_event = events[0]
    assert isinstance(recurred_event, RecurredEvent)
    assert ("<RecurredEvent datetime='2014-05-02 12:00:00+00:00' "
            "title=u'birthday'>" == repr(recurred_event))


def test_event__EventDateTime__1(address_book, EventFactory, DateTime):
    """A whole day event gets indexed as noon in timzone utc."""
    event = EventFactory(address_book,
                         datetime=DateTime(2015, 1, 5, 14, 14),
                         whole_day_event=True)
    adapter = IEventDateTime(event)
    assert DateTime(2015, 1, 5, 12) == adapter.datetime
    assert pytz.utc == adapter.datetime.tzinfo


def test_event___get_field_name_on_IEvent__1(address_book, FieldFactory):
    """It only returns the field name if the title type and the value match ...

    between event and recurring event.
    """
    event_field = FieldFactory(address_book, IEvent, u'Bool', u'foo')
    revent_field = FieldFactory(address_book, IRecurringEvent, u'Bool', u'foo')
    assert (event_field.__name__ ==
            _get_field_name_on_IEvent(revent_field, IEntity(IEvent)))


def test_event___get_field_name_on_IEvent__2(address_book, FieldFactory):
    """It returns `None` if the fields do not match exactly."""
    FieldFactory(address_book, IEvent, u'Choice', u'foo', values=[u'a'])
    revent_field = FieldFactory(
        address_book, IRecurringEvent, u'Choice', u'foo', values=[u'a', u'b'])
    assert None is _get_field_name_on_IEvent(revent_field, IEntity(IEvent))


def test_event___get_field_name_on_IEvent__3(zcmlS):
    """It returns the field name for a field defined on `IBaseEvent`."""
    assert 'category' == _get_field_name_on_IEvent(IRecurringEvent['category'],
                                                   IEntity(IEvent))


def test_event___get_field_name_on_IEvent__4(zcmlS):
    """It returns `None` for a field not defined on `IBaseEvent`."""
    assert None is _get_field_name_on_IEvent(IRecurringEvent['period'],
                                             IEntity(IEvent))


def test_event__get_event_data_from_recurring_event__1(
        address_book, CategoryFactory, RecurringEventFactory, DateTime):
    """It returns a dict of event data and datetime."""
    category = CategoryFactory(address_book, u'bar')
    recurring_event = RecurringEventFactory(
        address_book,
        category=category,
        period='weekly',
        datetime=DateTime(2014, 5, 24, 10, 30),
        alternative_title=u'foo bar')
    assert ({
        'alternative_title': u'foo bar',
        'category': category,
        'datetime': DateTime(2000, 1, 1, 10, 30),
        'external_persons': None,
        'persons': None,
        'text': None,
        'whole_day_event': False} == get_event_data_from_recurring_event(
            recurring_event, DateTime(2000, 1, 1, 10, 30)))


def test_event__get_event_data_from_recurring_event__2(
        address_book, CategoryFactory, RecurringEventFactory, DateTime):
    """It returns whole day events."""
    category = CategoryFactory(address_book, u'bar')
    recurring_event = RecurringEventFactory(
        address_book,
        category=category,
        period='weekly',
        datetime=DateTime(2014, 5, 24, 1),
        whole_day_event=True,
        alternative_title=u'foo bar')
    assert ({
        'alternative_title': u'foo bar',
        'category': category,
        'datetime': DateTime(2000, 1, 1, 1),
        'external_persons': None,
        'persons': None,
        'text': None,
        'whole_day_event': True} == get_event_data_from_recurring_event(
            recurring_event, DateTime(2000, 1, 1, 1)))


def test_event__get_event_data_from_recurring_event__3(
        address_book, FieldFactory, RecurringEventFactory, DateTime):
    """It returns the appropriate user defined fields."""
    revent_foo = FieldFactory(
        address_book, IRecurringEvent, u'Text', u'foo').__name__
    revent_bar = FieldFactory(
        address_book, IRecurringEvent, u'Text', u'bar').__name__
    FieldFactory(address_book, IEvent, u'Text', u'foo')
    recurring_event = RecurringEventFactory(
        address_book, **{
            revent_foo: u'asdf',
            revent_bar: u'qwe',
            'period': 'weekly',
            'datetime': DateTime(2014, 5, 24, 10, 30)})
    assert ({
        'Field-3': 'asdf',
        'alternative_title': None,
        'category': None,
        'datetime': DateTime(2000, 1, 1, 10, 30),
        'external_persons': None,
        'persons': None,
        'text': None,
        'whole_day_event': False} == get_event_data_from_recurring_event(
            recurring_event, DateTime(2000, 1, 1, 10, 30)))


def test_event__title__1(address_book, EventFactory):
    """It returns the alternative title if it is set."""
    event = EventFactory(address_book, alternative_title=u'alt-title')
    assert u'alt-title' == ITitle(event)


def test_event__title__2(address_book, CategoryFactory, EventFactory):
    """It returns the category title if the alternative title is not set."""
    event = EventFactory(
        address_book, category=CategoryFactory(address_book, u'birthday'))
    assert u'birthday' == ITitle(event)


def test_event__title__3(address_book, EventFactory):
    """It returns a string if neither alt. title nor category are set."""
    assert u'event' == ITitle(EventFactory(address_book))


def test_event__get_calendar__1(address_book, EventFactory):
    """It adapts an event to its calendar."""
    event = EventFactory(address_book)
    assert address_book.calendar == ICalendar(event)
