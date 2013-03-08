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

    def test_person_referenced_on_an_event_can_still_become_a_principal(self):
        # regression test
        self.fail('nyi')

    def test_if_a_person_cannot_be_deleted_it_might_be_referenced_in_cal(self):
        # regression test, move to i.ab --> fix error message.
        # (If a person cannot get deleted the reason migt be that he is
        # referenced in the calendar --> Test it in form &
        # SearchResultHandler + fix error message)
        self.fail('nyi')


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
