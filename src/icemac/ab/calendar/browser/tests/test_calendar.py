from mock import Mock
import icemac.ab.calendar.testing
import unittest


class CalendarSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for the calendar."""

    def test_visitor_is_able_to_access_the_calendar(self):
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab')
        browser.getLink('Calendar').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar', browser.url)
        self.assertIn('Sunday', browser.contents)

    def test_visitor_is_not_able_to_add_events(self):
        from mechanize import LinkNotFoundError
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        # No link to add events:
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('event').click()

    def test_anonymous_is_not_able_to_access_calendar(self):
        from icemac.addressbook.testing import Browser
        from zope.security.interfaces import Unauthorized
        browser = self.get_browser()
        browser.handleErrors = False  # needed to catch exception
        with self.assertRaises(Unauthorized):
            browser.open('http://localhost/ab/++attribute++calendar')


class CalendarFTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Testing ..calendar.Calendar."""

    def test_displays_current_month_by_default(self):
        import datetime
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        current_month = self.get_datetime().strftime('%B %Y')
        self.assertIn(current_month, browser.contents)

    def test_can_switch_to_entered_month(self):
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getControl('month').value = '05/2003'
        browser.getControl('Apply').click()
        self.assertIn('May 2003', browser.contents)
        self.assertEqual('05/2003', browser.getControl('month').value)
        self.assertEqual(['Month changed.'], browser.get_messages())

    def test_shows_events_belonging_to_month(self):
        from datetime import timedelta
        import transaction
        now = self.get_datetime()
        self.create_event(alternative_title=u'foo bar', datetime=now)
        self.create_event(alternative_title=u'baz qux',
                          datetime=now + timedelta(days=31))
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        self.assertIn('foo bar', browser.contents)
        self.assertNotIn('baz qux', browser.contents)


class EventDescriptionUTests(icemac.ab.calendar.testing.UnitTestCase):
    """Unit testing ..calendar.EventDescription."""

    def test_EventDescription_implements_IEventDescription(self):
        from zope.interface.verify import verifyObject
        from icemac.ab.calendar.browser.renderer.interfaces import (
            IEventDescription)
        from icemac.ab.calendar.browser.calendar import EventDescription

        event_description = self.get_event_description()
        self.assertIsInstance(event_description, EventDescription)
        self.assertTrue(verifyObject(IEventDescription, event_description))


class EventDescriptionFTests(icemac.ab.calendar.testing.ZCMLTestCase):
    """Functional testing ..calendar.EventDescription.persons."""

    def test_persons_is_komma_separated_list_of_persons_in_ab_and_externals(
            self):
        from icemac.addressbook.person import Person
        from icemac.addressbook.utils import create_obj
        p1 = create_obj(Person, last_name=u'Tester', first_name=u'Hans')
        p2 = create_obj(Person, last_name=u'Koch', first_name=u'Fritz')
        event_description = self.get_event_description(
            persons=set([p1, p2]),
            external_persons=[u'Klaus Arkpe', u'Heiner Myer'])
        self.assertEqual(u'Hans Tester, Fritz Koch, Klaus Arkpe, Heiner Myer',
                         event_description.persons)

    def test_persons_is_emtpty_string_if_there_are_no_persons_assigned(self):
        self.assertEqual(u'', self.get_event_description().persons)


class EventDescription_getText_Tests(icemac.ab.calendar.testing.UnitTestCase):
    """Testing ..calendar.EventDescription.getText()."""

    def _makeOne(self, category_name=None, **kw):
        from icemac.ab.calendar.category import Category
        from icemac.addressbook.utils import create_obj
        if category_name is not None:
            kw['category'] = create_obj(Category, title=category_name)
        return self.get_event_description(**kw)

    def callMUT(self, event_description, **kw):
        return event_description.getText(**kw)

    def test_returns_alternative_title(self):
        ed = self._makeOne(
            category_name=u'birthday', alternative_title=u'foo bar')
        self.assertEqual(u'foo bar', self.callMUT(ed))

    def test_returns_category_title_if_alternative_title_is_not_set(self):
        ed = self._makeOne(category_name=u'foo', alternative_title=None)
        self.assertEqual(u'foo', self.callMUT(ed))

    def test_returns_empty_if_neither_alternative_title_nor_category_is_set(
            self):
        ed = self._makeOne(category=None, alternative_title=None)
        self.assertEqual(u'', self.callMUT(ed))

    def test_getText_returns_not_hyphenated_text_by_default(self):
        self.assertEqual(
            u'birthday',
            self.callMUT(self._makeOne(alternative_title=u'birthday')))

    def test_getText_raises_UnknownLanguageError_for_unknown_languages(self):
        from ..renderer.interfaces import UnknownLanguageError
        with self.assertRaises(UnknownLanguageError):
            self.callMUT(self._makeOne(),lang='Clingon')

    def test_getText_returns_hyphenated_respecting_set_language(self):
        ed = self._makeOne(alternative_title=u'Geburtstag')
        self.assertEqual(u'Ge&shy;burts&shy;tag', self.callMUT(ed, lang='de'))
