from mock import Mock, patch, call
import icemac.ab.calendar.testing
import unittest


class TableUTests(unittest.TestCase):
    """Unit testing ..table.Table."""

    def test_Table_fulfills_IRenderer_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRenderer
        from ..table import Table
        self.assertTrue(verifyObject(IRenderer, Table(None, None, None)))


class TableITests(icemac.ab.calendar.testing.BrowserTestCase):
    """Integraion testing ..table.Table."""

    def test_two_events_at_the_same_time_are_rendered_with_one_time_dt(self):
        from datetime import date
        today = date.today()
        self.create_event(
            datetime=self.get_datetime((today.year, today.month, 22, 16, 14)),
            alternative_title=u'event1')
        self.create_event(
            datetime=self.get_datetime((today.year, today.month, 22, 16, 14)),
            alternative_title=u'event2')
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        self.assertEqual(1, len(browser.etree.xpath('//dt')))

    def test_weekdays_are_translated_to_language_of_customer(self):
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        self.assertNotIn('Sonntag', browser.contents)  # English locale
        browser.addHeader('Accept-Language', 'de-DE')
        browser.reload()
        self.assertIn('Sonntag', browser.contents)  # German locale

    def test_day_numbers_are_add_event_links_able_to_add_a_new_event(self):
        from datetime import date
        self.create_category(u'example')
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getLink('15').click()
        self.assertEqual('%s/15 00:00' % date.today().strftime('%y/%m'),
                         browser.getControl('datetime').value)
        browser.getControl('Add', index=1).click()
        self.assertEqual(['"example" added.'], browser.get_messages())

    def test_day_numbers_are_text_for_visitors(self):
        from mechanize import LinkNotFoundError
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/++attribute++calendar')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('15')


class TableEvent_text_Tests(icemac.ab.calendar.testing.UnitTestCase):
    """Testing ..table.TableEvent.text()."""

    def _make_one(self, text, lang):
        from ..table import TableEvent
        from ..interfaces import UnknownLanguageError
        view = TableEvent()
        view.context = Mock()
        view.context.getText.side_effect = [
            UnknownLanguageError, UnknownLanguageError, text]
        view.request = self.get_request(HTTP_ACCEPT_LANGUAGE=lang)
        return view

    def test_tries_to_find_lang_code_getText_understands(self):
        view = self._make_one('Foo', lang='de_DE')
        self.assertEqual('Foo', view.text())
        self.assertEqual([call(u'de_DE'), call(u'de'), call()],
                         view.context.getText.call_args_list)

    def test_returns_Edit_if_text_is_empty(self):
        # So the user can edit events with empty text.
        view = self._make_one('', lang='de_DE')
        self.assertEqual(u'Edit', view.text())


class TableEventITests(icemac.ab.calendar.testing.ZODBTestCase):
    """Integration testing ..table.TableEvent."""

    def setUp(self):
        super(TableEventITests, self).setUp()
        get_time_zone_name = (
            'icemac.addressbook.preferences.utils.get_time_zone_name')
        patcher = patch(get_time_zone_name)
        self.get_time_zone_name = patcher.start()
        self.get_time_zone_name.return_value = 'UTC'
        self.addCleanup(patcher.stop)

    def getVUT(
            self, event, field_names=[], time_zone_name=None, request_kw={}):
        from icemac.ab.calendar.browser.renderer.interfaces import (
            IEventDescription)
        from icemac.ab.calendar.interfaces import (
            ICalendarDisplaySettings, IEvent)
        from zope.component import getMultiAdapter
        request = self.get_request(**request_kw)
        ab = self.layer['addressbook']
        ICalendarDisplaySettings(ab.calendar).event_additional_fields = [
            IEvent[x] for x in field_names]
        event_description = IEventDescription(event)
        view = getMultiAdapter(
            (event_description, request), name='table-event')
        view._action_url = 'url:'
        return view

    def test_renders_no_selected_event_additional_field_as_nothing(self):
        event = self.create_event(datetime=self.get_datetime())
        self.assertNotEllipsis('...class="info"...',
                               self.getVUT(event, [])())

    def test_renders_single_selected_event_additional_field_not_as_list(self):
        event = self.create_event(datetime=self.get_datetime(),
                                  external_persons=[u'Foo', u'Bar'])
        self.assertEllipsis('...<span class="info">Bar, Foo</span>...',
                            self.getVUT(event, ['persons'])())

    def test_renders_multiple_selected_event_additional_fields_as_list(self):
        event = self.create_event(
            datetime=self.get_datetime(),
            external_persons=[u'Foo', u'Bar'], text=u'Cool!')
        self.assertEllipsis('''...\
        <ul class="info">
          <li>Bar, Foo</li>
          <li>Cool!</li>
        </ul>
        ...''', self.getVUT(event, ['persons', 'text'])())

    def test_time_is_converted_to_timezone_of_user(self):
        event = self.create_event(
            datetime=self.get_datetime((2013, 11, 2, 9, 27)))
        self.get_time_zone_name.return_value = 'Australia/Currie'
        self.assertEqual(u'20:27', self.getVUT(event).time())

    def test_time_renders_Uhr_if_requested_language_is_German(self):
        event = self.create_event(
            datetime=self.get_datetime((2013, 11, 2, 9, 47)))
        view = self.getVUT(event, request_kw={'HTTP_ACCEPT_LANGUAGE': 'de'})
        self.assertEqual(u'09:47 Uhr', view.time())

    def test_time_renders_Uhr_if_requested_language_is_English(self):
        event = self.create_event(
            datetime=self.get_datetime((2013, 11, 2, 9, 47)))
        view = self.getVUT(event, request_kw={'HTTP_ACCEPT_LANGUAGE': 'en'})
        self.assertEqual(u'9:47 AM', view.time())
