from mock import Mock, MagicMock, patch, sentinel, call
import icemac.ab.calendar.testing
import unittest


class TableUTests(unittest.TestCase):
    """Unit testing ..table.Table."""

    def test_Table_fulfills_IRenderer_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRenderer
        from ..table import Table
        self.assertTrue(verifyObject(IRenderer, Table(None, None, None)))

    @unittest.expectedFailure
    def test_weekdays_are_translated_to_language_of_customer(self):
        self.fail('nyi')


class TableFTests(icemac.ab.calendar.testing.ZCMLTestCase):
    """Functional testing ..table.Table."""

    def setUp(self):
        from icemac.addressbook.browser.interfaces import IAddressBookLayer
        super(TableFTests, self).setUp()
        self.request = self.get_request()

    def callVUT(self, events):
        from ..table import Table
        from gocept.month import Month
        table = Table(Month(2, 2013), self.request, events)
        return table()

    def getETree(self, html):
        from lxml.etree import HTML
        sugared_value = u'<div>' + html + u'</div>'
        return HTML(sugared_value)

    def test_two_events_at_the_same_time_are_rendered_with_one_time_dt(self):
        event1 = self.get_event_description(
            (2013, 2, 22, 16, 14), alternative_title='event1')
        event2 = self.get_event_description(
            (2013, 2, 22, 16, 14), alternative_title='event2')
        action_url = (
            'icemac.ab.calendar.browser.renderer.table.TableEvent.action_url')
        with patch(action_url):
            result = self.callVUT([event1, event2])
        self.assertEqual(1, len(self.getETree(result).xpath('//dt')))


class TableEventTests(unittest.TestCase):
    """Testing ..table.TableEvent."""

    @unittest.expectedFailure
    def test_renders_time_in_time_zone_of_user(self):
        self.fail('nyi')

    @unittest.expectedFailure
    def test_renders_Uhr_if_requested_language_is_German(self):
        self.fail('nyi')


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


class TableEventFTests(icemac.ab.calendar.testing.ZCMLTestCase):
    """Functional testing ..table.TableEvent."""

    def callVUT(self, event_description, request=None):
        from zope.component import getMultiAdapter
        if request is None:
            request = self.get_request()
        view = getMultiAdapter(
            (event_description, request), name='table-event')
        view._action_url = 'url:'
        return view()

    def test_renders_person_names(self):
        event_description = self.get_event_description(
            external_persons=[u'Foo', u'Bar'])
        self.assertIn('Foo, Bar', self.callVUT(event_description))
