# -*- coding: utf-8 -*-
import icemac.ab.calendar.testing
import unittest


class CalendarSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for the calendar."""

    def test_visitor_is_able_to_access_a_filled_calendar(self):
        from ..calendar import hyphenate
        from pyphen import Pyphen
        event = self.create_event(
            datetime=self.get_datetime(),
            alternative_title=u"Cousin's Birthday")
        browser = self.get_browser('cal-visitor')
        # We need to set a language as otherwise there will only be numbers
        # instead of week day names:
        browser.addHeader('Accept-Language', 'en')
        browser.open('http://localhost/ab')
        browser.getLink('Calendar').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar', browser.url)
        self.assertIn('Sunday', browser.contents)
        self.assertIn(hyphenate("Cousin's Birthday", Pyphen(lang='en')),
                      browser.contents)

    def test_visitor_is_able_to_change_the_time_zone(self):
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getLink('UTC').click()
        self.assertEqual('http://localhost/ab/++preferences++/ab.timeZone',
                         browser.url)
        browser.getControl('Time zone').displayValue = ['Indian/Christmas']
        browser.getControl('Apply').click()
        self.assertEqual(['Data successfully updated.'],
                         browser.get_messages())

    def test_visitor_is_not_able_to_add_events(self):
        from mechanize import LinkNotFoundError
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        # No link to add events:
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('event').click()

    def test_anonymous_is_not_able_to_access_calendar(self):
        from zope.security.interfaces import Unauthorized
        browser = self.get_browser()
        browser.handleErrors = False  # needed to catch exception
        with self.assertRaises(Unauthorized):
            browser.open('http://localhost/ab/++attribute++calendar')


class CalendarFTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Testing ..calendar.Calendar."""

    def test_displays_current_month_by_default(self):
        browser = self.get_browser('cal-visitor')
        # We need to explicitly set the language here because otherwise the
        # month name is not displayed:
        browser.addHeader('Accept-Language', 'en')
        browser.open('http://localhost/ab/++attribute++calendar')
        current_month = self.get_datetime().strftime('%B %Y')
        self.assertIn(current_month, browser.contents)

    def test_can_switch_to_entered_month(self):
        browser = self.get_browser('cal-visitor')
        # We need to explicitly set the language here because otherwise the
        # month name is not displayed:
        browser.addHeader('Accept-Language', 'en')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getControl('month').value = '05/2003'
        browser.getControl('Apply').click()
        self.assertIn('May 2003', browser.contents)
        self.assertEqual('05/2003', browser.getControl('month').value)
        self.assertEqual(['Month changed.'], browser.get_messages())

    def test_keeps_month_switched_to(self):
        browser = self.get_browser('cal-visitor')
        calendar_url = 'http://localhost/ab/++attribute++calendar'
        browser.open(calendar_url)
        browser.getControl('month').value = '05/2003'
        browser.getControl('Apply').click()
        self.assertEqual(['Month changed.'], browser.get_messages())
        browser.open(calendar_url)
        self.assertEqual('05/2003', browser.getControl('month').value)

    def test_shows_events_belonging_to_month(self):
        from datetime import timedelta
        now = self.get_datetime()
        self.create_event(alternative_title=u'foo bär', datetime=now)
        self.create_event(alternative_title=u'baz qux',
                          datetime=now + timedelta(days=31))
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        self.assertIn('foo bär', browser.contents)
        self.assertNotIn('baz qux', browser.contents)

    def test_renders_time_zone_user_has_set_in_prefs_as_link(self):
        from zope.component import getUtility
        from zope.preference.interfaces import IDefaultPreferenceProvider
        default_prefs = getUtility(IDefaultPreferenceProvider)
        default_prefs.getDefaultPreferenceGroup('ab.timeZone').time_zone = (
            'Pacific/Fiji')
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        self.assertEqual(
            'http://localhost/ab/++preferences++/ab.timeZone',
            browser.getLink('Pacific/Fiji').url)

    def test_translates_selected_month(self):
        browser = self.get_browser('cal-visitor')
        browser.addHeader('Accept-Language', 'de-DE')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getControl('month for display').value = '10/2013'
        browser.getControl('Apply').click()
        self.assertIn('<h2>Oktober 2013</h2>', browser.contents)


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
    """Functional testing ..calendar.EventDescription."""

    def test_persons_is_komma_separated_list_of_persons_in_ab_and_externals(
            self):
        from icemac.addressbook.person import Person
        from icemac.addressbook.utils import create_obj
        p1 = create_obj(Person, last_name=u'Tester', first_name=u'Hans')
        p2 = create_obj(Person, last_name=u'Koch', first_name=u'Fritz')
        event_description = self.get_event_description(
            persons=set([p1, p2]),
            external_persons=[u'Klaus Arkpe', u'Heiner Myer'])
        self.assertEqual(u'Fritz Koch, Hans Tester, Heiner Myer, Klaus Arkpe',
                         event_description.persons)

    def test_persons_is_emtpty_string_if_there_are_no_persons_assigned(self):
        self.assertEqual(u'', self.get_event_description().persons)


class EventDescriptionITests_getInfo(icemac.ab.calendar.testing.ZODBTestCase):
    """Integration testing ..calendar.EventDescription.getInfo()"""

    def _make_one(self, **kw):
        from icemac.ab.calendar.browser.renderer.interfaces import (
            IEventDescription)
        from icemac.addressbook.testing import create
        ab = self.layer['addressbook']
        event = create(
            ab, ab.calendar, 'icemac.ab.calendar.event.Event',
            return_obj=True, **kw)
        return IEventDescription(event)

    def _set_settings(self, *args):
        from icemac.ab.calendar.interfaces import (
            ICalendarDisplaySettings, IEvent)
        fields = []
        for arg in args:
            if isinstance(arg, basestring):
                arg = IEvent[arg]
            fields.append(arg)
        ab = self.layer['addressbook']
        ICalendarDisplaySettings(ab.calendar).event_additional_fields = fields

    def test_returns_list_of_selected_fields_as_unicodes(self):
        from icemac.ab.calendar.interfaces import IEvent
        from icemac.addressbook.interfaces import IEntity
        from icemac.addressbook.testing import create_field
        ab = self.layer['addressbook']
        reservations_name = create_field(
            ab, 'icemac.ab.calendar.event.Event', u'Int', u'reservations')
        event_entity = IEntity(IEvent)
        # Both user fields and pre-defined fields are possible
        self._set_settings('text', event_entity.getRawField(reservations_name))
        ed = self._make_one(
            **{'text': u'Event is not yet sure.', reservations_name: 50})
        self.assertEqual([u'Event is not yet sure.', u'50'], ed.getInfo())

    def test_omits_fields_with_None_value(self):
        self._set_settings('text')
        ed = self._make_one()
        self.assertIsNone(ed.context.text)
        self.assertEqual([], ed.getInfo())

    def test_omits_empty_string_values(self):
        self._set_settings('persons')
        ed = self._make_one()
        self.assertEqual('', ed.persons)
        self.assertEqual([], ed.getInfo())

    def test_does_not_omit_0_numbers(self):
        from icemac.ab.calendar.interfaces import IEvent
        from icemac.addressbook.interfaces import IEntity
        from icemac.addressbook.testing import create_field
        ab = self.layer['addressbook']
        num_name = create_field(
            ab, 'icemac.ab.calendar.event.Event', u'Int', u'num')
        event_entity = IEntity(IEvent)
        self._set_settings(event_entity.getRawField(num_name))
        ed = self._make_one(**{num_name: 0})
        self.assertEqual([u'0'], ed.getInfo())

    def test_returns_external_and_internal_persons_if_persons_selected(self):
        from icemac.addressbook.testing import create_person
        ab = self.layer['addressbook']
        p1 = create_person(ab, ab, u'Tester', first_name=u'Hans')
        self._set_settings('persons')
        ed = self._make_one(
            persons=set([p1]),
            external_persons=[u'Franz Vrozzek', u'Fritz Vrba'])
        self.assertEqual([u'Franz Vrozzek, Fritz Vrba, Hans Tester'],
                         ed.getInfo())

    def test_hyphenates_text(self):
        self._set_settings('text')
        ed = self._make_one(text=u'I contain longer words.')
        self.assertEqual([u'I con&shy;tain longer word&shy;s.'],
                         ed.getInfo(lang='en'))


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
            self.callMUT(self._makeOne(), lang='Clingon')

    def test_getText_returns_hyphenated_respecting_set_language(self):
        ed = self._makeOne(alternative_title=u'Geburtstag')
        self.assertEqual(u'Ge&shy;burts&shy;tag', self.callMUT(ed, lang='de'))


class HyphenatedTests(unittest.TestCase):
    """Testing ..calendar.hyphenated"""

    def test_encodes_text_as_html_even_if_not_hyphenating(self):
        from ..calendar import hyphenated

        @hyphenated
        def func(ignored):
            return u'<script>'

        self.assertEqual(u'&lt;script&gt;', func(any))

    def test_hyphenates_text_and_encodes_text_for_html(self):
        from ..calendar import hyphenated

        @hyphenated
        def func(ignored, lang=None):
            return u'Gebürtstag<>'

        res = func(any, lang='de')
        self.assertIsInstance(res, unicode)
        self.assertEqual(u'Ge&shy;bürts&shy;tag&lt;&gt;', res)
