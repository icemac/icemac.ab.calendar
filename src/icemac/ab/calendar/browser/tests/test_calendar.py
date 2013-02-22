from mock import Mock
import icemac.ab.calendar.testing
import unittest


class CalendarSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for the calendar."""

    def setUp(self):
        from icemac.addressbook.testing import Browser
        super(CalendarSecurity, self).setUp()
        self.browser = Browser()
        self.browser.login('cal-visitor')
        self.browser.open('http://localhost/ab')
        self.browser.getLink('Calendar').click()

    def test_visitor_is_able_to_access_the_calendar(self):
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar', self.browser.url)
        self.assertIn('Sunday', self.browser.contents)

    def test_visitor_is_not_able_to_add_events(self):
        from mechanize import LinkNotFoundError
        # No link to add events:
        with self.assertRaises(LinkNotFoundError):
            self.browser.getLink('event').click()

    def test_visitor_is_not_able_to_edit_events(self):
        # No edit link
        self.fail('nyi')

    def test_anonymous_is_not_able_to_access_calendar(self):
        from icemac.addressbook.testing import Browser
        from zope.security.interfaces import Unauthorized
        browser = Browser()
        browser.handleErrors = False  # needed to catch exception
        with self.assertRaises(Unauthorized):
            browser.open('http://localhost/ab/++attribute++calendar')


class CalendarFTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Testing ..calendar.Calendar."""

    def setUp(self):
        from icemac.addressbook.testing import Browser
        super(CalendarFTests, self).setUp()
        self.browser = Browser()
        self.browser.login('cal-visitor')
        self.browser.handleErrors = False
        self.browser.open('http://localhost/ab/++attribute++calendar')

    def test_displays_current_month_by_default(self):
        import datetime
        current_month = datetime.date.today().strftime('%B %Y')
        self.assertIn(current_month, self.browser.contents)

    def test_can_switch_to_entered_month(self):
        browser = self.browser
        browser.getControl('month').value = '05/2003'
        browser.getControl('Apply').click()
        self.assertIn('May 2003', self.browser.contents)
        self.assertEqual('05/2003', browser.getControl('month').value)
        self.assertEqual(['Month changed.'], browser.get_messages())

    def test_shows_events_belonging_to_month(self):
        from datetime import datetime, timedelta
        from pytz import utc
        import transaction
        now = datetime.now(tz=utc)
        self.create_event(alternative_title=u'foo bar', datetime=now)
        self.create_event(alternative_title=u'baz qux',
                          datetime=now + timedelta(days=31))
        transaction.commit()
        browser = self.browser
        browser.reload()
        self.assertIn('foo bar', browser.contents)
        self.assertNotIn('baz qux', browser.contents)

    def test_respects_language_of_request_in_hypenation(self):
        self.fail('nyi')  # Test using mock


class EventDescriptionMixIn(object):
    """Mix-in for testing ..calendar.EventDescription."""

    def _makeOne(self, **kw):
        from icemac.ab.calendar.browser.renderer.interfaces import (
            IEventDescription)
        event = self.create_event(**kw)
        self.event_description = IEventDescription(event)


class EventDescriptionTests(EventDescriptionMixIn,
                            icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..calendar.EventDescription."""

    def test_EventDescription_implements_IEventDescription(self):
        from zope.interface.verify import verifyObject
        from icemac.ab.calendar.browser.renderer.interfaces import (
            IEventDescription)
        from icemac.ab.calendar.browser.calendar import EventDescription

        self.assertTrue(verifyObject(
            IEventDescription, EventDescription(self.create_event())))


class EventDescription_getText_Tests(EventDescriptionMixIn,
                                     icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..calendar.EventDescription.getText()."""

    def callMUT(self, **kw):
        return self.event_description.getText(**kw)

    def test_returns_alternative_title(self):
        category = self.create_category(u'birthday')
        self._makeOne(alternative_title=u'foo bar', category=category)
        self.assertEqual(u'foo bar', self.callMUT())

    def test_returns_category_title_if_alternative_title_is_not_set(self):
        self._makeOne(category=self.create_category(u'foo'))
        self.assertEqual(u'foo', self.callMUT())

    def test_returns_empty_if_neither_alternative_title_nor_category_is_set(
            self):
        self._makeOne()
        self.assertEqual(u'', self.callMUT())

    def test_getText_returns_hyphenated_defaulting_to_english(self):
        self._makeOne(alternative_title=u'birthday')
        self.assertEqual(u'birth&shy;day', self.callMUT())

    def test_getText_returns_hyphenated_respecting_set_language(self):
        self._makeOne(alternative_title=u'Geburtstag')
        self.assertEqual(u'Ge&shy;burts&shy;tag', self.callMUT(lang='de'))
