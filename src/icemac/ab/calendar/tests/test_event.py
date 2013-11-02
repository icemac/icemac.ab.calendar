# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import icemac.ab.calendar.testing
import icemac.addressbook.testing
import unittest


class EventTests(unittest.TestCase):
    """Testing ..event.Event."""

    layer = icemac.addressbook.testing.ADDRESS_BOOK_UNITTESTS

    def test_event_implements_IEvent_interface(self):
        from gocept.reference.verify import verifyObject
        from icemac.ab.calendar.interfaces import IEvent
        from icemac.ab.calendar.event import Event
        self.assertTrue(verifyObject(IEvent, Event()))


class EventRTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Regression testing ..event.Event."""

    def test_person_referenced_on_an_event_can_still_become_a_principal(self):
        from icemac.addressbook.testing import (
            create_person, create_email_address)
        ab = self.layer['addressbook']
        person = create_person(ab, ab, u'Tester')
        create_email_address(ab, person, email=u'tester@example.com')
        event = self.create_event(persons=set([person]))
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
        browser.getControl('datetime').value = self.get_datetime().strftime(
            '%y/%m/%d %H:%M')
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
