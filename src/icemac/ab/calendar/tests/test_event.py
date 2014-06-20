# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
import icemac.ab.calendar.testing
import icemac.addressbook.testing
import unittest
import zope.catalog.interfaces
import zope.component


class EventUTests(unittest.TestCase):
    """Testing ..event.Event."""

    layer = icemac.addressbook.testing.ADDRESS_BOOK_UNITTESTS

    def test_event_implements_IEvent_interface(self):
        from gocept.reference.verify import verifyObject
        from icemac.ab.calendar.interfaces import IEvent
        from icemac.ab.calendar.event import Event
        self.assertTrue(verifyObject(IEvent, Event()))

    def test_recurring_events_implements_IRecurringEvents_interface(self):
        from gocept.reference.verify import verifyObject
        from icemac.ab.calendar.interfaces import IRecurringEvents
        from icemac.ab.calendar.event import RecurringEventContainer
        self.assertTrue(
            verifyObject(IRecurringEvents, RecurringEventContainer()))

    def test_recurring_event_implements_IRecurringEvent_interface(self):
        from gocept.reference.verify import verifyObject
        from icemac.ab.calendar.interfaces import IRecurringEvent
        from icemac.ab.calendar.event import RecurringEvent
        self.assertTrue(verifyObject(IRecurringEvent, RecurringEvent()))

    def test_recurred_event_implements_IRecurredEvent_interface(self):
        from gocept.reference.verify import verifyObject
        from icemac.ab.calendar.interfaces import IRecurredEvent
        from icemac.ab.calendar.event import RecurredEvent
        self.assertTrue(verifyObject(IRecurredEvent, RecurredEvent()))


class EventCatalogTests(icemac.ab.calendar.testing.ZODBTestCase):
    """Testing catatloging of events."""

    def setUp(self):
        super(EventCatalogTests, self).setUp()
        datetime = self.get_datetime()
        self.event = self.create_event(datetime=datetime)
        self.create_recurring_event(datetime=datetime)

    def test_event_gets_cataloged_but_not_recurring_event(self):
        from ..interfaces import DATE_INDEX
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        results = catalog.searchResults(**{DATE_INDEX: {'any': None}})
        self.assertEqual([self.event], list(results))


class TestRecurrStarEvent(icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..event.RecurringEvent and ..event.RecurredEvent"""

    def setUp(self):
        from icemac.addressbook.testing import create_person
        super(TestRecurrStarEvent, self).setUp()
        ab = self.layer['addressbook']
        category = self.create_category(u'birthday')
        person = create_person(ab, ab, u'Tester')
        self.recurring_event = self.create_recurring_event(
            datetime=self.get_datetime((2014, 5, 2)), category=category,
            period='weekly', persons=set([person]), text=u'foobar')

    def test_get_events_returns_iterable_of_RecurredEvent_instances(self):
        from ..event import RecurredEvent
        events = list(self.recurring_event.get_events(
            self.get_datetime((2014, 5, 1, 0)),
            self.get_datetime((2014, 5, 8, 0))))
        self.assertEqual(1, len(events))
        event = events[0]
        self.assertIsInstance(event, RecurredEvent)
        self.assertEqual('foobar', event.text)

    def test_RecurredEvent__create_from_copies_attributes_from_parameter(self):
        from ..event import RecurredEvent
        recurred_event = RecurredEvent.create_from(
            self.recurring_event, self.get_datetime((2014, 4, 12, 21)))
        self.assertEqual(
            self.get_datetime((2014, 4, 12, 21)), recurred_event.datetime)
        self.assertIn(list(self.recurring_event.persons)[0],
                      recurred_event.persons)
        self.assertEqual(
            self.recurring_event.category, recurred_event.category)
        self.assertEqual(
            self.layer['addressbook'].calendar, recurred_event.__parent__)
        self.assertEqual(self.recurring_event, recurred_event.recurring_event)


class GetFieldNameOnIEventTests(icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..event._get_field_name_on_IEvent()."""

    def callFUT(self, field_name):
        from ..event import _get_field_name_on_IEvent
        from ..interfaces import IEvent, IRecurringEvent
        from icemac.addressbook.interfaces import IEntity
        field = IEntity(IRecurringEvent).getRawField(field_name)
        return _get_field_name_on_IEvent(field, IEntity(IEvent))

    def create_field(self, interface, title, type, values=None):
        from icemac.addressbook.testing import create_field
        ab = self.layer['addressbook']
        return create_field(ab, interface, type, title, values=values)

    def test_only_returns_field_name_if_matching_on_title_type_and_value(self):
        from ..interfaces import IRecurringEvent, IEvent
        event_field = self.create_field(IEvent, u'foo', u'Bool')
        revent_field = self.create_field(IRecurringEvent, u'foo', u'Bool')
        self.assertEqual(event_field, self.callFUT(revent_field))

    def test_returns_None_if_field_does_not_exactly_match(self):
        from ..interfaces import IRecurringEvent, IEvent
        self.create_field(IEvent, u'foo', u'Choice', values=[u'a'])
        revent_field = self.create_field(
            IRecurringEvent, u'foo', u'Choice', values=[u'a', u'b'])
        self.assertIsNone(self.callFUT(revent_field))

    def test_returns_field_name_for_field_not_defined_on_IBaseEvent(self):
        self.assertEqual('category', self.callFUT('category'))

    def test_returns_None_for_field_not_defined_on_IBaseEvent(self):
        self.assertIsNone(self.callFUT('period'))


class GetEventDataFromRecurringEventTests(
        icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..event.get_event_data_from_recurring_event()."""

    def callFUT(self, recurring_event, datetime):
        from ..event import get_event_data_from_recurring_event
        return get_event_data_from_recurring_event(recurring_event, datetime)

    def test_returns_dict_of_event_data_and_datetime(self):
        category = self.create_category(u'bar')
        recurring_event = self.create_recurring_event(
            category=category,
            datetime=self.get_datetime((2014, 5, 24, 10, 30)),
            alternative_title=u'foo bar')
        self.assertEqual(
            {'alternative_title': u'foo bar',
             'category': category,
             'datetime': self.get_datetime((2000, 1, 1, 10, 30)),
             'external_persons': None,
             'persons': None,
             'text': None},
            self.callFUT(recurring_event, self.get_datetime((2000, 1, 1, 0))))

    def test_returns_appropriate_user_defined_fields(self):
        from icemac.addressbook.testing import create_field, create
        from icemac.ab.calendar.interfaces import IEvent, IRecurringEvent
        ab = self.layer['addressbook']
        revent_foo = create_field(ab, IRecurringEvent, u'Text', u'foo')
        revent_bar = create_field(ab, IRecurringEvent, u'Text', u'bar')
        create_field(ab, IEvent, u'Text', u'foo')
        recurring_event = create(
            ab, ab.calendar_recurring_events,
            'icemac.ab.calendar.event.RecurringEvent', return_obj=True,
            **{revent_foo: u'asdf', revent_bar: u'qwe',
               'datetime': self.get_datetime((2014, 5, 24, 10, 30))})
        self.assertEqual(
            {'Field-3': 'asdf',
             'alternative_title': None,
             'category': None,
             'datetime': self.get_datetime((2000, 1, 1, 10, 30)),
             'external_persons': None,
             'persons': None,
             'text': None},
            self.callFUT(recurring_event, self.get_datetime((2000, 1, 1, 0))))


class EventRTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Regression testing ..event.Event."""

    def test_person_referenced_on_an_event_can_still_become_a_principal(self):
        from icemac.addressbook.testing import (
            create_person, create_email_address)
        ab = self.layer['addressbook']
        person = create_person(ab, ab, u'Tester')
        create_email_address(ab, person, email=u'tester@example.com')
        self.create_event(persons=set([person]))
        browser = self.get_browser('mgr')
        browser.open(
            'http://localhost/ab/++attribute++principals/@@addPrincipal.html')
        # User referenced on event is still in the list of persons which
        # might become a principal:
        self.assertEqual(['Tester'],
                         browser.getControl('person').displayOptions)


class EventEntitySTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Smoke testing event as an entity."""

    def setUp(self):
        super(EventEntitySTests, self).setUp()
        self.create_category(u'Wedding')

    def test_a_new_field_can_be_added_and_used(self):
        browser = self.get_browser('mgr')
        browser.open('http://localhost/ab/++attribute++entities')
        # It is possbile to a a new field to an event:
        browser.getLink('Edit fields', index=8).click()
        self.assertEqual('http://localhost/ab/++attribute++entities/'
                         'icemac.ab.calendar.event.Event', browser.url)
        browser.getLink('field').click()
        browser.getControl('type').displayValue = ['integer number']
        browser.getControl('title').value = 'Number of reservations'
        browser.getControl('Add', index=1).click()
        self.assertEqual(
            ['"Number of reservations" added.'], browser.get_messages())
        # This new field can be used in the event add form:
        browser.open(
            'http://localhost/ab/++attribute++calendar/@@addEvent.html')
        browser.getControl('datetime').value = self.format_datetime(
            self.get_datetime())
        browser.getControl('event category').displayValue = ['Wedding']
        browser.getControl('Number of reservations').value = '42'
        browser.getControl('Add', index=1).click()
        self.assertEqual(['"Wedding" added.'], browser.get_messages())
        # And in the event edit form:
        browser.getLink('Wedding').click()
        self.assertEqual(
            '42', browser.getControl('Number of reservations').value)
        browser.getControl('Number of reservations').value = '41'
        browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], browser.get_messages())


class TitleTests(icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..event.title()."""

    def callAUT(self, **kw):
        from icemac.ab.calendar.event import Event
        from icemac.addressbook.utils import create_obj
        from icemac.addressbook.interfaces import ITitle
        event = create_obj(Event, **kw)
        return ITitle(event)

    def test_returns_alternative_title_if_set(self):
        self.assertEqual(u'alt-title',
                         self.callAUT(alternative_title=u'alt-title'))

    def test_returns_category_title_if_alternative_title_is_not_set(self):
        category = self.create_category(u'birthday')
        self.assertEqual(u'birthday', self.callAUT(category=category))

    def test_returns_string_if_alternative_title_and_category_not_set(self):
        self.assertEqual(u'event', self.callAUT())


class GetCalendarITests(icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..event.get_calendar()."""

    def test_event_can_be_adapted_to_calendar(self):
        from ..interfaces import ICalendar
        event = self.create_event()
        self.assertEqual(self.layer['addressbook'].calendar, ICalendar(event))
