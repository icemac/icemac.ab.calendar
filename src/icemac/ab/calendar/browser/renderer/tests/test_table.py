from datetime import date
from icemac.ab.calendar.browser.interfaces import IEventDescription
from icemac.ab.calendar.browser.interfaces import UnknownLanguageError
from icemac.ab.calendar.browser.renderer.interfaces import IRenderer
from icemac.ab.calendar.browser.renderer.table import Table, TableEvent
from icemac.ab.calendar.interfaces import ICalendarDisplaySettings, IEvent
from icemac.addressbook.interfaces import IEntity
from zope.testbrowser.browser import LinkNotFoundError
from mock import Mock, call
from zope.interface.verify import verifyObject
import lxml
import pytest
import zope.component


def test_table__Table__1():
    """Table_fulfills_IRenderer_interface."""
    assert verifyObject(IRenderer, Table(None, None, None))


def test_table__Table__render__1(
        address_book, browser, EventFactory, CategoryFactory, DateTime):
    """It renders two events at the same time with two `dt` elements."""
    today = date.today()
    EventFactory(address_book, alternative_title=u'event1',
                 datetime=DateTime(today.year, today.month, 22, 16, 14),
                 category=CategoryFactory(address_book, u'foo'))
    EventFactory(address_book, alternative_title=u'event2',
                 datetime=DateTime(today.year, today.month, 22, 16, 14),
                 category=CategoryFactory(address_book, u'bar'))
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    assert 2 == len(browser.etree.xpath('//dt'))


def test_table__Table__render__2(address_book, browser):
    """It translates weekdays into the language of the user."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    assert 'Sonntag' not in browser.contents  # default English locale
    browser.lang('de-DE')
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    assert 'Sonntag' in browser.contents  # switched to German locale


def test_table__Table__render__3(
        address_book, browser, CategoryFactory, DateTime):
    """It renders the day numbers as links to add a new event."""
    CategoryFactory(address_book, u'example')
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    assert browser.getLink('15').url.startswith(browser.EVENT_ADD_URL)
    browser.getLink('15').click()
    assert (DateTime.format(date.today().replace(day=15)) ==
            browser.getControl('date').value)
    assert '12:00' == browser.getControl('time').value
    # Whole day event:
    assert browser.getControl('yes').selected
    browser.getControl('Add', index=1).click()
    assert '"example" added.' == browser.message


def test_table__Table__render__4(address_book, browser):
    """It renders day numbers are text for visitors."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_OVERVIEW_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('15')


@pytest.fixture('function')
def TableEventUFactory(RequestFactory):
    """Create a `TableEvent` view set up with some mocks for unit testing."""
    def create_table_event(text, lang):
        view = TableEvent()
        view.context = Mock()
        view.context.getText.side_effect = [
            UnknownLanguageError, UnknownLanguageError, text]
        view.request = RequestFactory(HTTP_ACCEPT_LANGUAGE=lang)
        return view
    return create_table_event


def test_table__TableEvent__text__1(TableEventUFactory):
    """It tries to find a language code `getText` understands."""
    view = TableEventUFactory('Foo', 'de_DE')
    assert 'Foo' == view.text()
    assert ([call(u'de_DE'), call(u'de'), call()] ==
            view.context.getText.call_args_list)


def test_table__TableEvent__text__2(TableEventUFactory):
    """It returns "Edit" if the text is empty.

    So the user can edit events with empty text.
    """
    view = TableEventUFactory('', lang='de_DE')
    assert u'Edit' == view.text()


@pytest.fixture('function')
def TableEventIFactory(address_book, utc_time_zone_pref, RequestFactory):
    """Get a `TableEvent` view for integration testing."""
    def get_table_event(event, field_names=[], request_kw={}):
        request = RequestFactory(**request_kw)
        event_entity = IEntity(IEvent)
        ICalendarDisplaySettings(
            address_book.calendar).event_additional_fields = [
                event_entity.getRawField(x) for x in field_names]
        event_description = IEventDescription(event)
        return zope.component.getMultiAdapter(
            (event_description, request), name='table-event')
    return get_table_event


def test_table__TableEvent__render__1(
        address_book, EventFactory, DateTime, TableEventIFactory):
    """It renders nothing if no event additional field is selected."""
    event = EventFactory(address_book, datetime=DateTime.now)
    assert 'class="info"' not in TableEventIFactory(event, [])()


def test_table__TableEvent__render__2(
        address_book, EventFactory, DateTime, TableEventIFactory):
    """It renders a single selected event additional field not as a list."""
    event = EventFactory(address_book, datetime=DateTime.now,
                         external_persons=[u'Foo', u'Bar'])
    assert ('<span class="info">Bar, Foo</span>' in
            TableEventIFactory(event, ['persons'])())


def test_table__TableEvent__render__3(
        address_book, EventFactory, DateTime, TableEventIFactory):
    """It renders multiple selected event additional fields as a list."""
    event = EventFactory(address_book,
                         datetime=DateTime.now,
                         external_persons=[u'Foo', u'Bar'], text=u'Cool!')
    etree = lxml.etree.HTML(
        TableEventIFactory(event, ['persons', 'text'])())
    assert [
        'Bar, Foo',
        'Cool!'
    ] == etree.xpath('//ul[@class="info"]/li/text()')


def test_table__TableEvent__info_1(
        address_book, EventFactory, FieldFactory, DateTime,
        TableEventIFactory):
    """It renders user defined fields."""
    field_name = FieldFactory(
        address_book, IEvent, u'Int', u'reservations').__name__
    event = EventFactory(
        address_book,
        **{'datetime': DateTime.now, 'text': u'Text1', field_name: 42})
    assert ([{u'info': u'Text1'}, {u'info': u'42'}] ==
            TableEventIFactory(event, ['text', field_name]).info())


def test_table__TableEvent__time__1(
        address_book, EventFactory, DateTime, TableEventIFactory,
        TimeZonePrefFactory):
    """It converts the time to the time zone of the user."""
    event = EventFactory(
        address_book, datetime=DateTime(2013, 11, 2, 9, 27))
    TimeZonePrefFactory('Australia/Currie')
    assert u'20:27' == TableEventIFactory(event).time()


def test_table__TableEvent__time__2(
        address_book, EventFactory, DateTime, TableEventIFactory):
    """It renders "Uhr" if the requested language is German."""
    event = EventFactory(
        address_book, datetime=DateTime(2013, 11, 2, 9, 47))
    view = TableEventIFactory(event, request_kw={'HTTP_ACCEPT_LANGUAGE': 'de'})
    assert u'09:47 Uhr' == view.time()


def test_table__TableEvent__time__3(
        address_book, EventFactory, DateTime, TableEventIFactory):
    """It renders "AM" if the requested language is English."""
    event = EventFactory(
        address_book, datetime=DateTime(2013, 11, 2, 9, 47))
    view = TableEventIFactory(event, request_kw={'HTTP_ACCEPT_LANGUAGE': 'en'})
    assert u'9:47 AM' == view.time()


def test_table__TableEvent__time__4(
        address_book, EventFactory, DateTime, TableEventIFactory):
    """It renders a zero width space for a whole day event."""
    event = EventFactory(
        address_book, datetime=DateTime(2013, 11, 2, 18),
        whole_day_event=True)
    assert u'&#x200b;' == TableEventIFactory(event).time()
