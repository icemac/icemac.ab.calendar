from mock import Mock, patch, sentinel, call
import icemac.ab.calendar.testing
import unittest


class TableUTests(unittest.TestCase):
    """Unit testing ..table.Table."""

    def test_Table_fulfills_IRenderer_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRenderer
        from ..table import Table
        self.assertTrue(verifyObject(IRenderer, Table(None, None, None)))


class TableFTests(icemac.ab.calendar.testing.ZCMLTestCase):
    """Functional testing ..table.Table."""

    def setUp(self):
        from icemac.addressbook.browser.interfaces import IAddressBookLayer
        from zope.interface import alsoProvides
        from zope.publisher.browser import TestRequest
        super(TableFTests, self).setUp()
        self.request = TestRequest()
        alsoProvides(self.request, IAddressBookLayer)

    def callVUT(self, events):
        from ..table import Table
        from gocept.month import Month
        table = Table(Month(2, 2013), self.request, events)
        return table()

    def getETree(self, html):
        from lxml.etree import HTML
        sugared_value = u'<div>' + html + u'</div>'
        return HTML(sugared_value)

    def getEventDescription(self, time_tuple, **kw):
        from ...calendar import EventDescription
        from datetime import datetime
        event = Mock()
        event.datetime = datetime(*time_tuple)
        for key, value in kw.items():
            setattr(event, key, value)
        return EventDescription(event)

    def test_two_events_at_the_same_time_are_rendered_with_one_time_dt(self):
        event1 = self.getEventDescription(
            (2013, 2, 22, 16, 14), alternative_title='event1')
        event2 = self.getEventDescription(
            (2013, 2, 22, 16, 14), alternative_title='event2')
        action_url = (
            'icemac.ab.calendar.browser.renderer.table.TableEvent.action_url')
        with patch(action_url):
            result = self.callVUT([event1, event2])
        self.assertEqual(1, len(self.getETree(result).xpath('//dt')))


class TableEventTests(unittest.TestCase):
    """Testing ..table.TableEvent."""

    def test_renders_time_in_time_zone_of_user(self):
        self.fail('nyi')


class TableEvent_text_Tests(unittest.TestCase):
    """Testing ..table.TableEvent.text()."""

    def _make_one(self, lang):
        from ..table import TableEvent
        from ..interfaces import UnknownLanguageError
        from zope.publisher.browser import TestRequest
        view = TableEvent()
        view.context = Mock()
        view.context.getText.side_effect = [
            UnknownLanguageError, UnknownLanguageError, sentinel.val]
        view.request = TestRequest(HTTP_ACCEPT_LANGUAGE=lang)
        return view

    def test_tries_to_find_lang_code_getText_understands(self):
        view = self._make_one(lang='de_DE')
        self.assertEqual(sentinel.val, view.text())
        self.assertEqual([call(u'de_DE'), call(u'de'), call()],
                         view.context.getText.call_args_list)
